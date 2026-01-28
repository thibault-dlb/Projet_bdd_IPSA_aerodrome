from fastapi import FastAPI, Depends, HTTPException, status, Header
from typing import Annotated, List, Optional

from CRUD import DatabaseManager
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
) # Import all necessary models

# Security imports for authentication
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware Configuration
# This allows the frontend (running on a file:// or different domain)
# to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "Code_SQlite.db"

# Dependency to get a DB session
def get_db():
    db = DatabaseManager(DATABASE_URL)
    try:
        yield db
    finally:
        pass

# --- RBAC Dependencies ---

async def get_current_user(x_user_id: Optional[int] = Header(None), x_user_type: Optional[str] = Header(None)):
    if not x_user_id or not x_user_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return {"id": x_user_id, "type": x_user_type}

async def is_gestionnaire(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["type"] != "gestionnaire":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires administrator privileges")
    return current_user

async def is_agent(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["type"] not in ["agent", "gestionnaire"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires agent or administrator privileges")
    return current_user

async def is_pilote(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["type"] != "pilote":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires pilot privileges")
    return current_user

# Function to authenticate user
def authenticate_user(db: DatabaseManager, username: str, password: str):
    user_data = None
    user_type = None

    # Check in Pilote table
    pilote = db.select("Pilote", filters={"username": username})
    if pilote and verify_password(password, pilote[0]["password_hash"]):
        user_data = pilote[0]
        user_type = "pilote"
    
    if not user_data:
        # Check in Agent_d_exploitation table
        agent = db.select("Agent_d_exploitation", filters={"username": username})
        if agent and verify_password(password, agent[0]["password_hash"]):
            user_data = agent[0]
            user_type = "agent"

    if not user_data:
        # Check in Gestionnaire table
        gestionnaire = db.select("Gestionnaire", filters={"username": username})
        if gestionnaire and verify_password(password, gestionnaire[0]["password_hash"]):
            user_data = gestionnaire[0]
            user_type = "gestionnaire"

    if user_data:
        return {"id": user_data["Id"], "type": user_type, "name": user_data["username"]}
    return None

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Airport Management API"}

@app.post("/login/")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[DatabaseManager, Depends(get_db)]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Bearer"}, # Removed for consistency with header-based auth
        )
    return {"user_id": user["id"], "user_type": user["type"], "message": f"Welcome, {user['type']}!"}

# NOTE: AUTHENTICATION AND AUTHORIZATION
# For a production application, authentication and authorization mechanisms (e.g., OAuth2 with JWT tokens)
# would need to be implemented, especially for sensitive operations on 'Gestionnaire' and 'Agent_d_exploitation'
# tables. This would involve:
# - User registration and login endpoints.
# - Hashing passwords before storing them (e.g., using bcrypt).
# - Generating and validating access tokens.
# - Dependency functions to check user roles and permissions.
# These aspects are outside the scope of this basic CRUD API implementation but are crucial for security.

# -----------------------------------------------------------
# Carburant Endpoints
# -----------------------------------------------------------

@app.get("/carburants/", response_model=List[Carburant])
async def get_all_carburants(db: Annotated[DatabaseManager, Depends(get_db)]):
    carburants = db.select("Carburant")
    return carburants

@app.get("/carburants/{carburant_nom}", response_model=Carburant)
async def get_carburant(carburant_nom: str, db: Annotated[DatabaseManager, Depends(get_db)]):
    carburant = db.select("Carburant", filters={"Nom": carburant_nom})
    if not carburant:
        raise HTTPException(status_code=404, detail="Carburant not found")
    return carburant[0]

@app.post("/carburants/", response_model=Carburant, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_carburant(carburant: CarburantCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
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
async def update_carburant(carburant_nom: str, updated_data: CarburantCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Carburant", data=updated_data.model_dump(), filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    
    updated_carburant = db.select("Carburant", filters={"Nom": carburant_nom})
    return updated_carburant[0]

@app.delete("/carburants/{carburant_nom}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_carburant(carburant_nom: str, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Carburant", filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    return

# -----------------------------------------------------------
# Pilote Endpoints
# -----------------------------------------------------------

@app.get("/pilotes/", response_model=List[Pilote], dependencies=[Depends(is_agent)])
async def get_all_pilotes(db: Annotated[DatabaseManager, Depends(get_db)]):
    pilotes = db.select("Pilote")
    return pilotes

@app.get("/pilotes/{pilote_id}", response_model=Pilote)
async def get_pilote(pilote_id: int, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["type"] not in ["gestionnaire", "agent"] and current_user["id"] != pilote_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this pilot")
    pilote = db.select("Pilote", filters={"Id": pilote_id})
    if not pilote:
        raise HTTPException(status_code=404, detail="Pilote not found")
    return pilote[0]

@app.post("/pilotes/", response_model=Pilote, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_pilote(pilote: PiloteCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    user_data = pilote.model_dump()
    hashed_password = get_password_hash(user_data.pop("password"))
    user_data["password_hash"] = hashed_password
    
    new_id = db.create("Pilote", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Pilote with this username already exists or invalid data")
    
    created_pilote = db.select("Pilote", filters={"Id": new_id})
    if not created_pilote:
        raise HTTPException(status_code=500, detail="Failed to retrieve created pilote")
    return created_pilote[0]

@app.put("/pilotes/{pilote_id}", response_model=Pilote)
async def update_pilote(pilote_id: int, updated_data: PiloteCreate, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["type"] not in ["gestionnaire"] and current_user["id"] != pilote_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this pilot")
    rows_affected = db.update("Pilote", data=updated_data.model_dump(), filters={"Id": pilote_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Pilote not found")
    
    updated_pilote = db.select("Pilote", filters={"Id": pilote_id})
    return updated_pilote[0]

@app.delete("/pilotes/{pilote_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_pilote(pilote_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Pilote", filters={"Id": pilote_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Pilote not found")
    return

# -----------------------------------------------------------
# Infrastructure Endpoints
# -----------------------------------------------------------

@app.get("/infrastructures/", response_model=List[Infrastructure])
async def get_all_infrastructures(db: Annotated[DatabaseManager, Depends(get_db)]):
    infrastructures = db.select("Infrastructure")
    return infrastructures

@app.get("/infrastructures/{infra_id}", response_model=Infrastructure)
async def get_infrastructure(infra_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    infrastructure = db.select("Infrastructure", filters={"Id": infra_id})
    if not infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return infrastructure[0]

@app.post("/infrastructures/", response_model=Infrastructure, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_infrastructure(infrastructure: InfrastructureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Infrastructure", data=infrastructure.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_infrastructure = db.select("Infrastructure", filters={"Id": new_id})
    if not created_infrastructure:
        raise HTTPException(status_code=500, detail="Failed to retrieve created infrastructure")
    return created_infrastructure[0]

@app.put("/infrastructures/{infra_id}", response_model=Infrastructure, dependencies=[Depends(is_gestionnaire)])
async def update_infrastructure(infra_id: int, updated_data: InfrastructureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Infrastructure", data=updated_data.model_dump(), filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    updated_infrastructure = db.select("Infrastructure", filters={"Id": infra_id})
    return updated_infrastructure[0]

@app.delete("/infrastructures/{infra_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_infrastructure(infra_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Infrastructure", filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return

# -----------------------------------------------------------
# Avion Endpoints
# -----------------------------------------------------------

@app.get("/avions/", response_model=List[Avion], dependencies=[Depends(is_agent)])
async def get_all_avions(db: Annotated[DatabaseManager, Depends(get_db)]):
    avions = db.select("Avion")
    return avions

@app.get("/avions/{immatriculation}", response_model=Avion)
async def get_avion(immatriculation: str, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire", "agent"] and current_user["id"] != avion[0]["pilote_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this avion")
    return avion[0]

@app.post("/avions/", response_model=Avion, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_avion(avion: AvionCreate, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    avion_data = avion.model_dump()
    avion_data["pilote_id"] = current_user["id"]
    new_id = db.create("Avion", data=avion_data)
    # For text primary keys, new_id might be None even on success, so we check existence
    created_avion = db.select("Avion", filters={"Immatriculation": avion.Immatriculation})
    if not created_avion:
        raise HTTPException(status_code=400, detail="Avion with this immatriculation already exists or invalid data")
    return created_avion[0]

@app.put("/avions/{immatriculation}", response_model=Avion)
async def update_avion(immatriculation: str, updated_data: AvionCreate, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire"] and current_user["id"] != avion[0]["pilote_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this avion")
    rows_affected = db.update("Avion", data=updated_data.model_dump(exclude_unset=True), filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    
    updated_avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    return updated_avion[0]

@app.delete("/avions/{immatriculation}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avion(immatriculation: str, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        raise HTTPException(status_code=404, detail="Avion not found")
    if current_user["type"] not in ["gestionnaire"] and current_user["id"] != avion[0]["pilote_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this avion")
    rows_affected = db.delete("Avion", filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    return

# -----------------------------------------------------------
# Creneaux Endpoints
# -----------------------------------------------------------

@app.get("/creneaux/", response_model=List[Creneau], dependencies=[Depends(is_agent)])
async def get_all_creneaux(db: Annotated[DatabaseManager, Depends(get_db)]):
    creneaux = db.select("Creneaux")
    return creneaux

@app.get("/creneaux/{creneau_id}", response_model=Creneau)
async def get_creneau(creneau_id: int, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not creneau:
        raise HTTPException(status_code=404, detail="Creneau not found")
    if current_user["type"] not in ["gestionnaire", "agent"] and current_user["id"] != creneau[0]["pilote_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this creneau")
    return creneau[0]

from datetime import datetime, timedelta

# ... (other code)

def calculate_cout_total(db: DatabaseManager, creneau: CreneauCreate) -> float:
    total_cost = 0

    # Infrastructure cost
    if creneau.infrastructure_id:
        infra = db.select("Infrastructure", filters={"Id": creneau.infrastructure_id})
        if infra:
            infra = infra[0]
            debut = datetime.fromisoformat(creneau.debut_prevu)
            fin = datetime.fromisoformat(creneau.fin_prevu)
            duration = fin - debut
            days = duration.days
            
            if days >= 30:
                total_cost += (days / 30) * infra["prix_mois"]
            elif days >= 7:
                total_cost += (days / 7) * infra["prix_semaine"]
            else:
                total_cost += days * infra["prix_jour"]

    # Avitaillement cost
    if creneau.avitaillement_id:
        avitaillement = db.select("Avitaillement", filters={"Id": creneau.avitaillement_id})
        if avitaillement:
            total_cost += avitaillement[0]["cout"]

    return total_cost

@app.post("/creneaux/", response_model=Creneau, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_creneau(creneau: CreneauCreate, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    creneau_data = creneau.model_dump()
    creneau_data["pilote_id"] = current_user["id"]
    creneau_data["etat"] = "Demandé"
    creneau_data["cout_total"] = calculate_cout_total(db, creneau)

    # 90-minute interval check
    debut_prevu = datetime.fromisoformat(creneau.debut_prevu)
    fin_prevu = datetime.fromisoformat(creneau.fin_prevu)
    
    all_creneaux = db.select("Creneaux", filters={"infrastructure_id": creneau.infrastructure_id})
    for existing_creneau in all_creneaux:
        existing_debut = datetime.fromisoformat(existing_creneau["debut_prevu"])
        existing_fin = datetime.fromisoformat(existing_creneau["fin_prevu"])
        
        # Check for overlap, considering the 90-minute margin
        if (debut_prevu < existing_fin + timedelta(minutes=90)) and (fin_prevu > existing_debut - timedelta(minutes=90)):
            raise HTTPException(status_code=409, detail="Time slot conflicts with an existing one (including 90-minute security interval)")

    new_id = db.create("Creneaux", data=creneau_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_creneau = db.select("Creneaux", filters={"Id": new_id})
    if not created_creneau:
        raise HTTPException(status_code=500, detail="Failed to retrieve created creneau")
    return created_creneau[0]

@app.put("/creneaux/{creneau_id}", response_model=Creneau, dependencies=[Depends(is_agent)])
async def update_creneau(creneau_id: int, updated_data: CreneauCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    existing_creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not existing_creneau:
        raise HTTPException(status_code=404, detail="Creneau not found")

    # Etat lifecycle check
    current_etat = existing_creneau[0]["etat"]
    new_etat = updated_data.etat
    valid_transitions = {
        "Demandé": ["Confirmé", "Annulé"],
        "Confirmé": ["Autorisé", "Annulé"],
        "Autorisé": ["Achevé"],
        "Achevé": [],
        "Annulé": []
    }

    if new_etat != current_etat and new_etat not in valid_transitions.get(current_etat, []):
        raise HTTPException(status_code=400, detail=f"Invalid state transition from {current_etat} to {new_etat}")
    
    update_data = updated_data.model_dump(exclude_unset=True)
    update_data["cout_total"] = calculate_cout_total(db, updated_data)

    rows_affected = db.update("Creneaux", data=update_data, filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    
    updated_creneau = db.select("Creneaux", filters={"Id": creneau_id})
    return updated_creneau[0]

@app.delete("/creneaux/{creneau_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_creneau(creneau_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Creneaux", filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    return

# -----------------------------------------------------------
# Gestionnaire Endpoints
# -----------------------------------------------------------

@app.get("/gestionnaires/", response_model=List[Gestionnaire], dependencies=[Depends(is_gestionnaire)])
async def get_all_gestionnaires(db: Annotated[DatabaseManager, Depends(get_db)]):
    gestionnaires = db.select("Gestionnaire")
    return gestionnaires

@app.get("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire, dependencies=[Depends(is_gestionnaire)])
async def get_gestionnaire(gestionnaire_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not gestionnaire:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return gestionnaire[0]

@app.post("/gestionnaires/", response_model=Gestionnaire, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_gestionnaire(gestionnaire: GestionnaireCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    user_data = gestionnaire.model_dump()
    hashed_password = get_password_hash(user_data.pop("password"))
    user_data["password_hash"] = hashed_password

    new_id = db.create("Gestionnaire", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_gestionnaire = db.select("Gestionnaire", filters={"Id": new_id})
    if not created_gestionnaire:
        raise HTTPException(status_code=500, detail="Failed to retrieve created gestionnaire")
    return created_gestionnaire[0]

@app.put("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire, dependencies=[Depends(is_gestionnaire)])
async def update_gestionnaire(gestionnaire_id: int, updated_data: GestionnaireCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Gestionnaire", data=updated_data.model_dump(exclude_unset=True), filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    
    updated_gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not updated_gestionnaire:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated gestionnaire")
    return updated_gestionnaire[0]

@app.delete("/gestionnaires/{gestionnaire_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_gestionnaire(gestionnaire_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Gestionnaire", filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return

# -----------------------------------------------------------
# Agent_d_exploitation Endpoints
# -----------------------------------------------------------

@app.get("/agents/", response_model=List[AgentExploitation], dependencies=[Depends(is_agent)])
async def get_all_agents(db: Annotated[DatabaseManager, Depends(get_db)]):
    agents = db.select("Agent_d_exploitation")
    return agents

@app.get("/agents/{agent_id}", response_model=AgentExploitation, dependencies=[Depends(is_agent)])
async def get_agent(agent_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return agent[0]

@app.post("/agents/", response_model=AgentExploitation, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_gestionnaire)])
async def create_agent(agent: AgentExploitationCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    user_data = agent.model_dump()
    hashed_password = get_password_hash(user_data.pop("password"))
    user_data["password_hash"] = hashed_password

    new_id = db.create("Agent_d_exploitation", data=user_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_agent = db.select("Agent_d_exploitation", filters={"Id": new_id})
    if not created_agent:
        raise HTTPException(status_code=500, detail="Failed to retrieve created agent d'exploitation")
    return created_agent[0]

@app.put("/agents/{agent_id}", response_model=AgentExploitation, dependencies=[Depends(is_agent)])
async def update_agent(agent_id: int, updated_data: AgentExploitationCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Agent_d_exploitation", data=updated_data.model_dump(exclude_unset=True), filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    
    updated_agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not updated_agent:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated agent d'exploitation")
    return updated_agent[0]

@app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_agent(agent_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Agent_d_exploitation", filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return

# -----------------------------------------------------------
# Facture Endpoints
# -----------------------------------------------------------

@app.get("/factures/", response_model=List[Facture], dependencies=[Depends(is_agent)])
async def get_all_factures(db: Annotated[DatabaseManager, Depends(get_db)]):
    factures = db.select("Facture")
    return factures

@app.get("/factures/{facture_id}", response_model=Facture)
async def get_facture(facture_id: int, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    facture = db.select("Facture", filters={"Id": facture_id})
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    
    if current_user["type"] not in ["gestionnaire", "agent"]:
        # Check if the pilot is associated with this facture
        creneaux = db.select("Creneaux", filters={"facture_id": facture_id, "pilote_id": current_user["id"]})
        if not creneaux:
            raise HTTPException(status_code=403, detail="Not authorized to view this facture")

    return facture[0]

@app.post("/factures/", response_model=Facture, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_agent)])
async def create_facture(facture: FactureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Facture", data=facture.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_facture = db.select("Facture", filters={"Id": new_id})
    if not created_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve created facture")
    return created_facture[0]

@app.put("/factures/{facture_id}", response_model=Facture, dependencies=[Depends(is_agent)])
async def update_facture(facture_id: int, updated_data: FactureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Facture", data=updated_data.model_dump(exclude_unset=True), filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    
    updated_facture = db.select("Facture", filters={"Id": facture_id})
    if not updated_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated facture")
    return updated_facture[0]

@app.delete("/factures/{facture_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_agent)])
async def delete_facture(facture_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Facture", filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    return

# -----------------------------------------------------------
# Messagerie Endpoints
# -----------------------------------------------------------

@app.get("/messageries/", response_model=List[Messagerie], dependencies=[Depends(is_agent)])
async def get_all_messageries(db: Annotated[DatabaseManager, Depends(get_db)]):
    messageries = db.select("Messagerie")
    return messageries

@app.get("/messageries/{message_id}", response_model=Messagerie)
async def get_messagerie(message_id: int, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not messagerie:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg = messagerie[0]
    if current_user["type"] not in ["gestionnaire", "agent"] and not (current_user["id"] == msg["pilote_id"] or current_user["id"] == msg["agent_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this message")
        
    return msg

@app.post("/messageries/", response_model=Messagerie, status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_pilote)])
async def create_messagerie(messagerie: MessagerieCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Messagerie", data=messagerie.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_messagerie = db.select("Messagerie", filters={"Id": new_id})
    if not created_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve created message")
    return created_messagerie[0]

@app.put("/messageries/{message_id}", response_model=Messagerie)
async def update_messagerie(message_id: int, updated_data: MessagerieCreate, db: Annotated[DatabaseManager, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not messagerie:
        raise HTTPException(status_code=404, detail="Message not found")

    msg = messagerie[0]
    if current_user["type"] not in ["gestionnaire", "agent"] and not (current_user["id"] == msg["pilote_id"] or current_user["id"] == msg["agent_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this message")

    rows_affected = db.update("Messagerie", data=updated_data.model_dump(exclude_unset=True), filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    updated_messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not updated_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated message")
    return updated_messagerie[0]

@app.delete("/messageries/{message_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_gestionnaire)])
async def delete_messagerie(message_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Messagerie", filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return