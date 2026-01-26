# pyright: reportMissingImports=false
# This comment tells Pylance to ignore missing import warnings.
# It is used here because the imports are correctly handled by the virtual environment,
# but Pylance might not always pick it up automatically.

# api/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated, List
from pathlib import Path

# Assuming CRUD.py is in the parent directory
import sys
sys.path.append(str(Path(__file__).parent.parent))

from CRUD import DatabaseManager
from api.models import (
    Carburant, CarburantCreate, CarburantBase, 
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
    allow_origins=["http://127.0.0.1:5500"],  # Specifically allow the VS Code Live Server origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

DATABASE_URL = "Code_SQlite.db"

# Dependency to get a DB session
def get_db():
    db = DatabaseManager(DATABASE_URL)
    try:
        yield db
    finally:
        pass

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
        return {"id": user_data["Id"], "type": user_type}
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
            headers={"WWW-Authenticate": "Bearer"},
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

@app.post("/carburants/", response_model=Carburant, status_code=status.HTTP_201_CREATED)
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

@app.put("/carburants/{carburant_nom}", response_model=Carburant)
async def update_carburant(carburant_nom: str, updated_data: CarburantCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Carburant", data=updated_data.model_dump(), filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    
    updated_carburant = db.select("Carburant", filters={"Nom": carburant_nom})
    return updated_carburant[0]

@app.delete("/carburants/{carburant_nom}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carburant(carburant_nom: str, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Carburant", filters={"Nom": carburant_nom})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Carburant not found")
    return

# -----------------------------------------------------------
# Pilote Endpoints
# -----------------------------------------------------------

@app.get("/pilotes/", response_model=List[Pilote])
async def get_all_pilotes(db: Annotated[DatabaseManager, Depends(get_db)]):
    pilotes = db.select("Pilote")
    return pilotes

@app.get("/pilotes/{pilote_id}", response_model=Pilote)
async def get_pilote(pilote_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    pilote = db.select("Pilote", filters={"Id": pilote_id})
    if not pilote:
        raise HTTPException(status_code=404, detail="Pilote not found")
    return pilote[0]

@app.post("/pilotes/", response_model=Pilote, status_code=status.HTTP_201_CREATED)
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
async def update_pilote(pilote_id: int, updated_data: PiloteCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Pilote", data=updated_data.model_dump(), filters={"Id": pilote_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Pilote not found")
    
    updated_pilote = db.select("Pilote", filters={"Id": pilote_id})
    return updated_pilote[0]

@app.delete("/pilotes/{pilote_id}", status_code=status.HTTP_204_NO_CONTENT)
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

@app.post("/infrastructures/", response_model=Infrastructure, status_code=status.HTTP_201_CREATED)
async def create_infrastructure(infrastructure: InfrastructureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Infrastructure", data=infrastructure.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_infrastructure = db.select("Infrastructure", filters={"Id": new_id})
    if not created_infrastructure:
        raise HTTPException(status_code=500, detail="Failed to retrieve created infrastructure")
    return created_infrastructure[0]

@app.put("/infrastructures/{infra_id}", response_model=Infrastructure)
async def update_infrastructure(infra_id: int, updated_data: InfrastructureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Infrastructure", data=updated_data.model_dump(), filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    updated_infrastructure = db.select("Infrastructure", filters={"Id": infra_id})
    return updated_infrastructure[0]

@app.delete("/infrastructures/{infra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_infrastructure(infra_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Infrastructure", filters={"Id": infra_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return

# -----------------------------------------------------------
# Avion Endpoints
# -----------------------------------------------------------

@app.get("/avions/", response_model=List[Avion])
async def get_all_avions(db: Annotated[DatabaseManager, Depends(get_db)]):
    avions = db.select("Avion")
    return avions

@app.get("/avions/{immatriculation}", response_model=Avion)
async def get_avion(immatriculation: str, db: Annotated[DatabaseManager, Depends(get_db)]):
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        raise HTTPException(status_code=404, detail="Avion not found")
    return avion[0]

@app.post("/avions/", response_model=Avion, status_code=status.HTTP_201_CREATED)
async def create_avion(avion: AvionCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Avion", data=avion.model_dump())
    # For text primary keys, new_id might be None even on success, so we check existence
    created_avion = db.select("Avion", filters={"Immatriculation": avion.Immatriculation})
    if not created_avion:
        raise HTTPException(status_code=400, detail="Avion with this immatriculation already exists or invalid data")
    return created_avion[0]

@app.put("/avions/{immatriculation}", response_model=Avion)
async def update_avion(immatriculation: str, updated_data: AvionCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Avion", data=updated_data.model_dump(exclude_unset=True), filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    
    updated_avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    return updated_avion[0]

@app.delete("/avions/{immatriculation}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avion(immatriculation: str, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Avion", filters={"Immatriculation": immatriculation})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Avion not found")
    return

# -----------------------------------------------------------
# Creneaux Endpoints
# -----------------------------------------------------------

@app.get("/creneaux/", response_model=List[Creneau])
async def get_all_creneaux(db: Annotated[DatabaseManager, Depends(get_db)]):
    creneaux = db.select("Creneaux")
    return creneaux

@app.get("/creneaux/{creneau_id}", response_model=Creneau)
async def get_creneau(creneau_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not creneau:
        raise HTTPException(status_code=404, detail="Creneau not found")
    return creneau[0]

@app.post("/creneaux/", response_model=Creneau, status_code=status.HTTP_201_CREATED)
async def create_creneau(creneau: CreneauCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Creneaux", data=creneau.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_creneau = db.select("Creneaux", filters={"Id": new_id})
    if not created_creneau:
        raise HTTPException(status_code=500, detail="Failed to retrieve created creneau")
    return created_creneau[0]

@app.put("/creneaux/{creneau_id}", response_model=Creneau)
async def update_creneau(creneau_id: int, updated_data: CreneauCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Creneaux", data=updated_data.model_dump(exclude_unset=True), filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    
    updated_creneau = db.select("Creneaux", filters={"Id": creneau_id})
    return updated_creneau[0]

@app.delete("/creneaux/{creneau_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creneau(creneau_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Creneaux", filters={"Id": creneau_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Creneau not found")
    return

# -----------------------------------------------------------
# Gestionnaire Endpoints
# -----------------------------------------------------------

@app.get("/gestionnaires/", response_model=List[Gestionnaire])
async def get_all_gestionnaires(db: Annotated[DatabaseManager, Depends(get_db)]):
    gestionnaires = db.select("Gestionnaire")
    return gestionnaires

@app.get("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire)
async def get_gestionnaire(gestionnaire_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not gestionnaire:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return gestionnaire[0]

@app.post("/gestionnaires/", response_model=Gestionnaire, status_code=status.HTTP_201_CREATED)
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

@app.put("/gestionnaires/{gestionnaire_id}", response_model=Gestionnaire)
async def update_gestionnaire(gestionnaire_id: int, updated_data: GestionnaireCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Gestionnaire", data=updated_data.model_dump(exclude_unset=True), filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    
    updated_gestionnaire = db.select("Gestionnaire", filters={"Id": gestionnaire_id})
    if not updated_gestionnaire:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated gestionnaire")
    return updated_gestionnaire[0]

@app.delete("/gestionnaires/{gestionnaire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gestionnaire(gestionnaire_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Gestionnaire", filters={"Id": gestionnaire_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    return

# -----------------------------------------------------------
# Agent_d_exploitation Endpoints
# -----------------------------------------------------------

@app.get("/agents/", response_model=List[AgentExploitation])
async def get_all_agents(db: Annotated[DatabaseManager, Depends(get_db)]):
    agents = db.select("Agent_d_exploitation")
    return agents

@app.get("/agents/{agent_id}", response_model=AgentExploitation)
async def get_agent(agent_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return agent[0]

@app.post("/agents/", response_model=AgentExploitation, status_code=status.HTTP_201_CREATED)
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

@app.put("/agents/{agent_id}", response_model=AgentExploitation)
async def update_agent(agent_id: int, updated_data: AgentExploitationCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Agent_d_exploitation", data=updated_data.model_dump(exclude_unset=True), filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    
    updated_agent = db.select("Agent_d_exploitation", filters={"Id": agent_id})
    if not updated_agent:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated agent d'exploitation")
    return updated_agent[0]

@app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Agent_d_exploitation", filters={"Id": agent_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Agent d'exploitation not found")
    return

# -----------------------------------------------------------
# Facture Endpoints
# -----------------------------------------------------------

@app.get("/factures/", response_model=List[Facture])
async def get_all_factures(db: Annotated[DatabaseManager, Depends(get_db)]):
    factures = db.select("Facture")
    return factures

@app.get("/factures/{facture_id}", response_model=Facture)
async def get_facture(facture_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    facture = db.select("Facture", filters={"Id": facture_id})
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    return facture[0]

@app.post("/factures/", response_model=Facture, status_code=status.HTTP_201_CREATED)
async def create_facture(facture: FactureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Facture", data=facture.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_facture = db.select("Facture", filters={"Id": new_id})
    if not created_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve created facture")
    return created_facture[0]

@app.put("/factures/{facture_id}", response_model=Facture)
async def update_facture(facture_id: int, updated_data: FactureCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Facture", data=updated_data.model_dump(exclude_unset=True), filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    
    updated_facture = db.select("Facture", filters={"Id": facture_id})
    if not updated_facture:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated facture")
    return updated_facture[0]

@app.delete("/factures/{facture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facture(facture_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Facture", filters={"Id": facture_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Facture not found")
    return

# -----------------------------------------------------------
# Messagerie Endpoints
# -----------------------------------------------------------

@app.get("/messageries/", response_model=List[Messagerie])
async def get_all_messageries(db: Annotated[DatabaseManager, Depends(get_db)]):
    messageries = db.select("Messagerie")
    return messageries

@app.get("/messageries/{message_id}", response_model=Messagerie)
async def get_messagerie(message_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not messagerie:
        raise HTTPException(status_code=404, detail="Message not found")
    return messagerie[0]

@app.post("/messageries/", response_model=Messagerie, status_code=status.HTTP_201_CREATED)
async def create_messagerie(messagerie: MessagerieCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    new_id = db.create("Messagerie", data=messagerie.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Invalid data or creation failed")
    
    created_messagerie = db.select("Messagerie", filters={"Id": new_id})
    if not created_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve created message")
    return created_messagerie[0]

@app.put("/messageries/{message_id}", response_model=Messagerie)
async def update_messagerie(message_id: int, updated_data: MessagerieCreate, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.update("Messagerie", data=updated_data.model_dump(exclude_unset=True), filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    updated_messagerie = db.select("Messagerie", filters={"Id": message_id})
    if not updated_messagerie:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated message")
    return updated_messagerie[0]

@app.delete("/messageries/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_messagerie(message_id: int, db: Annotated[DatabaseManager, Depends(get_db)]):
    rows_affected = db.delete("Messagerie", filters={"Id": message_id})
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return