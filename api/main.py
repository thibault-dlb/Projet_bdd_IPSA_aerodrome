"""
⭐ API FASTAPI - SYSTÈME DE GESTION D'AÉRODROME ⭐

ARCHITECTURE SIMPLIFIÉE POUR PRÉSENTATION:
- FastAPI pour l'API REST
- JWT pour l'authentification
- 3 types d'utilisateurs avec RBAC (Gestionnaire, Agent, Pilote)
- Logique métier séparée dans business.py
- Base de données SQLite avec CRUD.py

FONCTIONNALITÉS CLÉS:
1. Authentification multi-rôles (ligne 130+)
2. Gestion des créneaux avec règle des 90 minutes (ligne 380+)
3. Calcul automatique de facturation (dans business.py)
4. CRUD complet pour toutes les entités
"""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from typing import Annotated, List, Optional
from datetime import datetime, timedelta

from CRUD import DatabaseManager
from business import (
    authenticate_user,
    hash_password,
    calculate_creneau_cost,
    validate_creneau_time_slot,
    validate_creneau_state_transition,
    get_user_avions,
    get_user_creneaux,
    check_user_owns_avion,
    check_user_owns_creneau,
    check_user_access_to_facture,
    check_user_access_to_message
)
from api.models import (
    Carburant, CarburantCreate,
    Pilote, PiloteCreate,
    Infrastructure, InfrastructureCreate,
    Avion, AvionCreate,
    Creneau, CreneauCreate,
    Gestionnaire, GestionnaireCreate,
    AgentExploitation, AgentExploitationCreate,
    Facture, FactureCreate,
    Messagerie, MessagerieCreate
)

# Imports pour l'authentification JWT
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Modèle Pydantic pour la réponse du token JWT
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_type: str

# Configuration JWT
SECRET_KEY = "YOUR_SUPER_SECRET_KEY"  # Pour la démo uniquement
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT avec expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user_with_hashed_password(user_data_model) -> dict:
    """Hash le password avec bcrypt avant insertion en BDD"""
    user_data = user_data_model.model_dump()
    hashed_password = hash_password(user_data.pop("password"))
    user_data["password_hash"] = hashed_password
    return user_data

# Initialisation de l'application FastAPI
app = FastAPI(title="API Gestion Aérodrome", version="1.0")

# Configuration CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "Code_SQlite.db"


# ============================================================
# ⭐ RBAC - CONTRÔLE D'ACCÈS BASÉ SUR LES RÔLES ⭐
# ============================================================

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Décode le JWT et retourne les infos utilisateur"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        user_type: str = payload.get("user_type")
        username: str = payload.get("sub")
        if user_id is None or user_type is None or username is None:
            raise CredentialsException
    except JWTError:
        raise CredentialsException
    
    return {"id": user_id, "type": user_type, "username": username}

async def is_gestionnaire(current_user: Annotated[dict, Depends(get_current_active_user)]):
    """Vérifie que l'utilisateur est un gestionnaire (niveau 0)"""
    if current_user["type"] != "gestionnaire":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires administrator privileges")
    return current_user

async def is_agent(current_user: Annotated[dict, Depends(get_current_active_user)]):
    """Vérifie que l'utilisateur est un agent ou gestionnaire (niveau 0-1)"""
    if current_user["type"] not in ["agent", "gestionnaire"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires agent or administrator privileges")
    return current_user

async def is_pilote(current_user: Annotated[dict, Depends(get_current_active_user)]):
    """Vérifie que l'utilisateur est un pilote (niveau 2)"""
    if current_user["type"] != "pilote":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires pilot privileges")
    return current_user


# ============================================================
# ⭐ ENDPOINTS API ⭐
# ============================================================

@app.get("/")
async def read_root():
    return {"message": "API Gestion Aérodrome - FastAPI + SQLite"}

# ⭐ ENDPOINT AUTHENTIFICATION ⭐
@app.post("/login/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authentifie un utilisateur (Pilote/Agent/Gestionnaire) et retourne un JWT.
    Utilise la fonction authenticate_user() de business.py qui vérifie avec bcrypt.
    """
    db = DatabaseManager(DATABASE_URL)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["name"], "user_id": user["id"], "user_type": user["type"]}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user["id"],
        "user_type": user["type"]
    }


# ============================================================
# ENDPOINTS CARBURANT
# ============================================================

@app.get("/carburants/", response_model=List[Carburant])
async def get_all_carburants():
    db = DatabaseManager(DATABASE_URL)
    carburants = db.select("Carburant")
    return carburants

@app.get("/carburants/{carburant_nom}", response_model=Carburant)
async def get_carburant(carburant_nom: str):
    db = DatabaseManager(DATABASE_URL)
    carburant = db.select("Carburant", filters={"Nom": carburant_nom})
    if not carburant:
        raise HTTPException(status_code=404, detail="Carburant not found")
    return carburant[0]

@app.post("/carburants/", response_model=Carburant, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_carburant(carburant: CarburantCreate):
    db = DatabaseManager(DATABASE_URL)
    new_id = db.create("Carburant", data=carburant.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Carburant with this name already exists or invalid data")
    
    # SQLite often uses the primary key directly for text-based PKs without `lastrowid`
    # For 'Carburant', 'Nom' is the PK, so we retrieve it directly
    created_carburant = db.select("Carburant", filters={"Nom": carburant.Nom})
    if not created_carburant:
        raise HTTPException(status_code=500, detail="Failed to retrieve created carburant")
    return created_carburant[0]

@app.put("/carburants/{carburant_nom}", response_model=Carburant, dependencies=[Depends(is_agent)])
async def update_carburant(carburant_nom: str, updated_data: CarburantCreate):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.update("Carburant", data=updated_data.model_dump(), filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    
    updated_carburant = db.select("Carburant", filters={"Nom": carburant_nom})
    return updated_carburant[0]

@app.delete("/carburants/{carburant_nom}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_carburant(carburant_nom: str):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Carburant", filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    return

# -----------------------------------------------------------
# Pilote Endpoints
# -----------------------------------------------------------

@app.get("/pilotes/", response_model=List[Pilote], dependencies=[Depends(is_agent)])
async def get_all_pilotes():
    db = DatabaseManager(DATABASE_URL)
    pilotes = db.select("Pilote")
    return pilotes

@app.get("/pilotes/{pilote_id}", response_model=Pilote)
async def get_pilote(pilote_id: int, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    if current_user["type"] not in ["gestionnaire", "agent"] and current_user["id"] != pilote_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this pilot")
    pilote = db.select("Pilote", filters={"Id": pilote_id})
    if not pilote:
        raise HTTPException(status_code=404, detail="Pilote not found")
    return Pilote(**pilote[0])

@app.post("/pilotes/", response_model=Pilote, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_pilote(pilote: PiloteCreate):
    db = DatabaseManager(DATABASE_URL)
    user_data = create_user_with_hashed_password(pilote)
    
    new_id = db.create("Pilote", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Pilote with this username already exists or invalid data")
    
    created_pilote = db.select("Pilote", filters={"Id": new_id})
    if not created_pilote:
        raise HTTPException(status_code=500, detail="Failed to retrieve created pilote")
    return created_pilote[0]

@app.put("/pilotes/{pilote_id}", response_model=Pilote)
async def update_pilote(pilote_id: int, updated_data: PiloteCreate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    if current_user["type"] not in ["gestionnaire"] and current_user["id"] != pilote_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this pilot")
    
    # Exclure le password des mises à jour
    update_dict = updated_data.model_dump(exclude={"password"})
    rows_affected = db.update("Pilote", data=update_dict, filters={"Id": pilote_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Pilote not found")
    
    updated_pilote = db.select("Pilote", filters={"Id": pilote_id})
    return updated_pilote[0]

@app.delete("/pilotes/{pilote_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_pilote(pilote_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Pilote", filters={"Id": pilote_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Pilote not found")
    return

# -----------------------------------------------------------
# Infrastructure Endpoints
# -----------------------------------------------------------

@app.get("/infrastructures/", response_model=List[Infrastructure])
async def get_all_infrastructures():
    db = DatabaseManager(DATABASE_URL)
    infrastructures = db.select("Infrastructure")
    return infrastructures

@app.get("/infrastructures/{infra_id}", response_model=Infrastructure)
async def get_infrastructure(infra_id: int):
    db = DatabaseManager(DATABASE_URL)
    infrastructure = db.select("Infrastructure", filters={"Id": infra_id})
    if not infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return infrastructure[0]

@app.post("/infrastructures/", response_model=Infrastructure, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_infrastructure(infrastructure: InfrastructureCreate):
    db = DatabaseManager(DATABASE_URL)
    new_id = db.create("Infrastructure", data=infrastructure.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_infrastructure = db.select("Infrastructure", filters={"Id": new_id})
    if not created_infrastructure:
        raise HTTPException(status_code=500, detail="Failed to retrieve created infrastructure")
    return created_infrastructure[0]

@app.put("/infrastructures/{infra_id}", response_model=Infrastructure, dependencies=[Depends(is_gestionnaire)])
async def update_infrastructure(infra_id: int, updated_data: InfrastructureCreate):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.update("Infrastructure", data=updated_data.model_dump(), filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    updated_infrastructure = db.select("Infrastructure", filters={"Id": infra_id})
    return updated_infrastructure[0]

@app.delete("/infrastructures/{infra_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_infrastructure(infra_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Infrastructure", filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return

# -----------------------------------------------------------
# Avion Endpoints
# -----------------------------------------------------------

@app.get("/avions/", response_model=List[Avion], dependencies=[Depends(is_agent)])
async def get_all_avions():
    db = DatabaseManager(DATABASE_URL)
    avions = db.select("Avion")
    return avions

@app.get("/avions/{immatriculation}", response_model=Avion)
async def get_avion(immatriculation: str, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire", "agent"] and not check_user_owns_avion(db, current_user["id"], immatriculation):
        raise HTTPException(status_code=403, detail="Not authorized to view this avion")
    return avion[0]

@app.post("/avions/", response_model=Avion, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_avion(avion: AvionCreate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    avion_data = avion.model_dump()
    avion_data["pilote_id"] = current_user["id"]
    new_id = db.create("Avion", data=avion_data)
    # For text primary keys, new_id might be None even on success, so we check existence
    created_avion = db.select("Avion", filters={"Immatriculation": avion.Immatriculation})
    if not created_avion:
        raise HTTPException(status_code=400, detail="Avion with this immatriculation already exists or invalid data")
    return created_avion[0]

@app.put("/avions/{immatriculation}", response_model=Avion)
async def update_avion(immatriculation: str, updated_data: AvionCreate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    if not db.select("Avion", filters={"Immatriculation": immatriculation}):
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire"] and not check_user_owns_avion(db, current_user["id"], immatriculation):
        raise HTTPException(status_code=403, detail="Not authorized to update this avion")
    rows_affected = db.update("Avion", data=updated_data.model_dump(exclude_unset=True), filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    
    updated_avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    return updated_avion[0]

@app.delete("/avions/{immatriculation}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avion(immatriculation: str, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    if not db.select("Avion", filters={"Immatriculation": immatriculation}):
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire"] and not check_user_owns_avion(db, current_user["id"], immatriculation):
        raise HTTPException(status_code=403, detail="Not authorized to delete this avion")
    rows_affected = db.delete("Avion", filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    return

@app.get("/pilotes/me/avions/", response_model=List[Avion])
async def get_my_avions(current_user: Annotated[dict, Depends(is_pilote)]):
    db = DatabaseManager(DATABASE_URL)
    return get_user_avions(db, current_user["id"])

@app.get("/pilotes/me/creneaux/", response_model=List[Creneau])
async def get_my_creneaux(current_user: Annotated[dict, Depends(is_pilote)]):
    db = DatabaseManager(DATABASE_URL)
    return get_user_creneaux(db, current_user["id"])

# ============================================================
# ⭐ ENDPOINTS CRÉNEAUX - RÈGLE DES 90 MINUTES ⭐
# ============================================================

@app.get("/creneaux/", response_model=List[Creneau], dependencies=[Depends(is_agent)])
async def get_all_creneaux():
    """Liste tous les créneaux (Agents et Gestionnaires uniquement)"""
    db = DatabaseManager(DATABASE_URL)
    creneaux = db.select("Creneaux")
    return creneaux

@app.get("/creneaux/{creneau_id}", response_model=Creneau)
async def get_creneau(creneau_id: int, current_user: Annotated[dict, Depends(get_current_active_user)]):
    """Récupère un créneau (avec vérification de propriété pour les pilotes)"""
    db = DatabaseManager(DATABASE_URL)
    creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not creneau:
        raise HTTPException(status_code=404, detail="Creneau not found")
    if current_user["type"] not in ["gestionnaire", "agent"] and not check_user_owns_creneau(db, current_user["id"], creneau_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this creneau")
    return creneau[0]

@app.post("/creneaux/", response_model=Creneau, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_creneau(creneau: CreneauCreate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    """
    ⭐ CRÉATION DE CRÉNEAU AVEC VALIDATION 90 MINUTES ⭐
    1. Vérifie qu'il n'y a pas de conflit avec les créneaux existants (+ 90 min de marge)
    2. Calcule automatiquement le coût total
    3. Crée le créneau avec l'état "Demandé"
    """
    db = DatabaseManager(DATABASE_URL)
    
    # ⭐ VALIDATION DE LA RÈGLE DES 90 MINUTES ⭐
    is_valid, error_msg = validate_creneau_time_slot(
        db, 
        creneau.infrastructure_id, 
        creneau.debut_prevu, 
        creneau.fin_prevu
    )
    if not is_valid:
        raise HTTPException(status_code=409, detail=error_msg)
    
    # Préparer les données du créneau
    creneau_data = creneau.model_dump()
    creneau_data["pilote_id"] = current_user["id"]
    creneau_data["etat"] = "Demandé"
    
    # ⭐ CALCUL AUTOMATIQUE DU COÛT ⭐
    creneau_data["cout_total"] = calculate_creneau_cost(
        db,
        creneau.infrastructure_id,
        creneau.avitaillement_id,
        creneau.debut_prevu,
        creneau.fin_prevu
    )

    new_id = db.create("Creneaux", data=creneau_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_creneau = db.select("Creneaux", filters={"Id": new_id})
    if not created_creneau:
        raise HTTPException(status_code=500, detail="Failed to retrieve created creneau")
    return created_creneau[0]

@app.put("/creneaux/{creneau_id}", response_model=Creneau, dependencies=[Depends(is_agent)])
async def update_creneau(creneau_id: int, updated_data: CreneauCreate):
    """
    Mise à jour d'un créneau (Agents uniquement).
    Recalcule le coût si les dates ou infrastructures changent.
    """
    db = DatabaseManager(DATABASE_URL)
    existing_creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not existing_creneau:
        raise HTTPException(status_code=404, detail="Creneau not found")

    # Validate state transition
    current_etat = existing_creneau[0]["etat"]
    is_valid, error_msg = validate_creneau_state_transition(current_etat, updated_data.etat)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    update_data = updated_data.model_dump(exclude_unset=True)
    update_data["cout_total"] = calculate_creneau_cost(
        db,
        updated_data.infrastructure_id,
        updated_data.avitaillement_id,
        updated_data.debut_prevu,
        updated_data.fin_prevu
    )

    rows_affected = db.update("Creneaux", data=update_data, filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    
    updated_creneau = db.select("Creneaux", filters={"Id": creneau_id})
    return updated_creneau[0]

@app.delete("/creneaux/{creneau_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_creneau(creneau_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Creneaux", filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    return

# -----------------------------------------------------------
# Gestionnaire Endpoints
# -----------------------------------------------------------

@app.get("/gestionnaires/", response_model=List[Gestionnaire], dependencies=[Depends(is_gestionnaire)])
async def get_all_gestionnaires():
    db = DatabaseManager(DATABASE_URL)
    gestionnaires = db.select("Gestionnaire")
    return gestionnaires

@app.get("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire, dependencies=[Depends(is_gestionnaire)])
async def get_gestionnaire(gestionnaire_id: int):
    db = DatabaseManager(DATABASE_URL)
    gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not gestionnaire:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return gestionnaire[0]

@app.post("/gestionnaires/", response_model=Gestionnaire, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_gestionnaire(gestionnaire: GestionnaireCreate):
    db = DatabaseManager(DATABASE_URL)
    user_data = create_user_with_hashed_password(gestionnaire)

    new_id = db.create("Gestionnaire", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_gestionnaire = db.select("Gestionnaire", filters={"Id": new_id})
    if not created_gestionnaire:
        raise HTTPException(status_code=500, detail="Failed to retrieve created gestionnaire")
    return created_gestionnaire[0]

@app.put("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire, dependencies=[Depends(is_gestionnaire)])
async def update_gestionnaire(gestionnaire_id: int, updated_data: GestionnaireCreate):
    db = DatabaseManager(DATABASE_URL)
    # Exclure le password des mises à jour
    update_dict = updated_data.model_dump(exclude={"password"})
    rows_affected = db.update("Gestionnaire", data=update_dict, filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    
    updated_gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not updated_gestionnaire:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated gestionnaire")
    return updated_gestionnaire[0]

@app.delete("/gestionnaires/{gestionnaire_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_gestionnaire(gestionnaire_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Gestionnaire", filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return

# -----------------------------------------------------------
# Agent_d_exploitation Endpoints
# -----------------------------------------------------------

@app.get("/agents/", response_model=List[AgentExploitation], dependencies=[Depends(is_agent)])
async def get_all_agents():
    db = DatabaseManager(DATABASE_URL)
    agents = db.select("Agent_d_exploitation")
    return agents

@app.get("/agents/{agent_id}", response_model=AgentExploitation, dependencies=[Depends(is_agent)])
async def get_agent(agent_id: int):
    db = DatabaseManager(DATABASE_URL)
    agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return agent[0]

@app.post("/agents/", response_model=AgentExploitation, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_agent(agent: AgentExploitationCreate):
    db = DatabaseManager(DATABASE_URL)
    user_data = create_user_with_hashed_password(agent)

    new_id = db.create("Agent_d_exploitation", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_agent = db.select("Agent_d_exploitation", filters={"Id": new_id})
    if not created_agent:
        raise HTTPException(status_code=500, detail="Failed to retrieve created agent d'exploitation")
    return created_agent[0]

@app.put("/agents/{agent_id}", response_model=AgentExploitation, dependencies=[Depends(is_agent)])
async def update_agent(agent_id: int, updated_data: AgentExploitationCreate):
    db = DatabaseManager(DATABASE_URL)
    # Exclure le password des mises à jour
    update_dict = updated_data.model_dump(exclude={"password"})
    rows_affected = db.update("Agent_d_exploitation", data=update_dict, filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    
    updated_agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not updated_agent:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated agent d'exploitation")
    return updated_agent[0]

@app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_agent(agent_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Agent_d_exploitation", filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return

# -----------------------------------------------------------
# Facture Endpoints
# -----------------------------------------------------------

@app.get("/factures/", response_model=List[Facture], dependencies=[Depends(is_agent)])
async def get_all_factures():
    db = DatabaseManager(DATABASE_URL)
    factures = db.select("Facture")
    return factures

@app.get("/factures/{facture_id}", response_model=Facture)
async def get_facture(facture_id: int, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    facture = db.select("Facture", filters={"Id": facture_id})
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    
    if current_user["type"] not in ["gestionnaire", "agent"]:
        if not check_user_access_to_facture(db, current_user["id"], facture_id):
            raise HTTPException(status_code=403, detail="Not authorized to view this facture")

    return facture[0]

@app.post("/factures/", response_model=Facture, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_facture(facture: FactureCreate):
    db = DatabaseManager(DATABASE_URL)
    new_id = db.create("Facture", data=facture.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_facture = db.select("Facture", filters={"Id": new_id})
    if not created_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve created facture")
    return created_facture[0]

@app.put("/factures/{facture_id}", response_model=Facture, dependencies=[Depends(is_agent)])
async def update_facture(facture_id: int, updated_data: FactureCreate):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.update("Facture", data=updated_data.model_dump(exclude_unset=True), filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    
    updated_facture = db.select("Facture", filters={"Id": facture_id})
    if not updated_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated facture")
    return updated_facture[0]

@app.delete("/factures/{facture_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_facture(facture_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Facture", filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    return

# -----------------------------------------------------------
# Messagerie Endpoints
# -----------------------------------------------------------

@app.get("/messageries/", response_model=List[Messagerie], dependencies=[Depends(is_agent)])
async def get_all_messageries():
    db = DatabaseManager(DATABASE_URL)
    messageries = db.select("Messagerie")
    return messageries

@app.get("/messageries/{message_id}", response_model=Messagerie)
async def get_messagerie(message_id: int, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not messagerie:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if current_user["type"] not in ["gestionnaire", "agent"] and not check_user_access_to_message(db, current_user["id"], message_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this message")
        
    return messagerie[0]

@app.post("/messageries/", response_model=Messagerie, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_messagerie(messagerie: MessagerieCreate):
    db = DatabaseManager(DATABASE_URL)
    new_id = db.create("Messagerie", data=messagerie.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_messagerie = db.select("Messagerie", filters={"Id": new_id})
    if not created_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve created message")
    return created_messagerie[0]

@app.put("/messageries/{message_id}", response_model=Messagerie)
async def update_messagerie(message_id: int, updated_data: MessagerieCreate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    db = DatabaseManager(DATABASE_URL)
    if not db.select("Messagerie", filters={"Id": message_id}):
        raise HTTPException(status_code=404, detail="Message not found")

    if current_user["type"] not in ["gestionnaire", "agent"] and not check_user_access_to_message(db, current_user["id"], message_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this message")

    rows_affected = db.update("Messagerie", data=updated_data.model_dump(exclude_unset=True), filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    updated_messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not updated_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated message")
    return updated_messagerie[0]

@app.delete("/messageries/{message_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_messagerie(message_id: int):
    db = DatabaseManager(DATABASE_URL)
    rows_affected = db.delete("Messagerie", filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return