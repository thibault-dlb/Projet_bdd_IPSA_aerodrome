# api/models.py
from pydantic import BaseModel
from typing import Optional, List

# Carburant
class CarburantBase(BaseModel):
    Nom: str
    prix_par_l: float

class CarburantCreate(CarburantBase):
    pass

class Carburant(CarburantBase):
    # No additional fields for the full model, but good to have for consistency
    class Config:
        from_attributes = True

# Infrastructure
class InfrastructureBase(BaseModel):
    nom: str
    type: str
    capacite_max: int
    prix_jour: float
    prix_semaine: float
    prix_mois: float

class InfrastructureCreate(InfrastructureBase):
    pass

class Infrastructure(InfrastructureBase):
    Id: int
    class Config:
        from_attributes = True

# Pilote
class PiloteBase(BaseModel):
    nom: str
    prenom: str
    tel: str
    mail: str
    username: str
    license: str
    medical: str
    password: str

class PiloteCreate(PiloteBase):
    pass

class Pilote(PiloteBase):
    Id: int
    class Config:
        from_attributes = True

# Avion
class AvionBase(BaseModel):
    Immatriculation: str
    marque: str
    modele: str
    dimension: str
    poids: str
    carburant_id: Optional[str] = None
    pilote_id: Optional[int] = None

class AvionCreate(AvionBase):
    pass

class Avion(AvionBase):
    class Config:
        from_attributes = True

# Creneaux
class CreneauBase(BaseModel):
    debut_prevu: str
    fin_prevu: str
    debut_reel: Optional[str] = None
    fin_reel: Optional[str] = None
    etat: str
    cout_total: Optional[float] = None
    avitaillement_id: Optional[int] = None
    pilote_id: Optional[int] = None
    infrastructure_id: Optional[int] = None
    facture_id: Optional[int] = None

class CreneauCreate(CreneauBase):
    pass

class Creneau(CreneauBase):
    Id: int
    class Config:
        from_attributes = True

# Gestionnaire
class GestionnaireBase(BaseModel):
    nom: str
    prenom: str
    tel: str
    mail: str
    password: str
    username: str

class GestionnaireCreate(GestionnaireBase):
    pass

class Gestionnaire(GestionnaireBase):
    Id: int
    class Config:
        from_attributes = True

# Agent_d_exploitation
class AgentExploitationBase(BaseModel):
    nom: str
    prenom: str
    tel: str
    mail: str
    username: str
    password: str

class AgentExploitationCreate(AgentExploitationBase):
    pass

class AgentExploitation(AgentExploitationBase):
    Id: int
    class Config:
        from_attributes = True

# Avitaillement
class AvitaillementBase(BaseModel):
    date: str
    heure: str
    quantite_en_l: float
    cout: float
    avion_id: str

class AvitaillementCreate(AvitaillementBase):
    pass

class Avitaillement(AvitaillementBase):
    Id: int
    class Config:
        from_attributes = True

# Facture
class FactureBase(BaseModel):
    rib: str
    date_d_emission: str
    agent_id: Optional[int] = None

class FactureCreate(FactureBase):
    pass

class Facture(FactureBase):
    Id: int
    class Config:
        from_attributes = True

# Messagerie
class MessagerieBase(BaseModel):
    date: str
    heure: str
    contenu: str
    sens_d_envoie: int
    agent_id: Optional[int] = None
    pilote_id: Optional[int] = None

class MessagerieCreate(MessagerieBase):
    pass

class Messagerie(MessagerieBase):
    Id: int
    class Config:
        from_attributes = True
