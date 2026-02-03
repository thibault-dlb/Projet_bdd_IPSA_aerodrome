#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Business logic layer - Contains all business rules and validations
No direct SQL queries - only calls to CRUD operations

FONCTIONS PRINCIPALES POUR LA PRÉSENTATION:
1. authenticate_user() - Authentification multi-rôles
2. validate_creneau_time_slot() - Règle métier des 90 minutes
3. calculate_creneau_cost() - Calcul automatique de facturation
4. hash_password() - Sécurité avec bcrypt
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from passlib.context import CryptContext

from CRUD import DatabaseManager

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    ⭐ SÉCURITÉ BCRYPT ⭐
    Hash un mot de passe avec bcrypt pour stockage sécurisé.
    """
    return pwd_context.hash(password)


def authenticate_user(db: DatabaseManager, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    ⭐ AUTHENTIFICATION MULTI-RÔLES ⭐
    Vérifie les credentials dans les 3 tables utilisateurs (Pilote, Agent, Gestionnaire)
    Utilise bcrypt pour la vérification sécurisée des mots de passe.
    
    Args:
        db: Database manager instance
        username: Nom d'utilisateur
        password: Mot de passe en clair
        
    Returns:
        Dict avec {id, type, name} si authentifié, None sinon
    """
    # Vérifier dans la table Pilote
    pilote = db.select("Pilote", filters={"username": username})
    if pilote and verify_password(password, pilote[0]["password_hash"]):
        return {"id": pilote[0]["Id"], "type": "pilote", "name": pilote[0]["username"]}
    
    # Vérifier dans la table Agent_d_exploitation
    agent = db.select("Agent_d_exploitation", filters={"username": username})
    if agent and verify_password(password, agent[0]["password_hash"]):
        return {"id": agent[0]["Id"], "type": "agent", "name": agent[0]["username"]}

    # Vérifier dans la table Gestionnaire
    gestionnaire = db.select("Gestionnaire", filters={"username": username})
    if gestionnaire and verify_password(password, gestionnaire[0]["password_hash"]):
        return {"id": gestionnaire[0]["Id"], "type": "gestionnaire", "name": gestionnaire[0]["username"]}

    return None


def calculate_creneau_cost(db: DatabaseManager, infrastructure_id: Optional[int], 
                          avitaillement_id: Optional[int], 
                          debut_prevu: str, fin_prevu: str) -> float:
    """
    ⭐ CALCUL AUTOMATIQUE DE FACTURATION ⭐
    Calcule le coût total d'un créneau : location infrastructure + avitaillement.
    Tarification dégressive : jour/semaine/mois selon la durée.
    
    Args:
        db: Database manager instance
        infrastructure_id: ID de l'infrastructure louée
        avitaillement_id: ID de l'opération d'avitaillement
        debut_prevu: Début (format ISO)
        fin_prevu: Fin (format ISO)
        
    Returns:
        Coût total en float
    """
    total_cost = 0.0

    # Calcul du coût d'infrastructure
    if infrastructure_id:
        infra = db.select("Infrastructure", filters={"Id": infrastructure_id})
        if infra:
            infra = infra[0]
            debut = datetime.fromisoformat(debut_prevu)
            fin = datetime.fromisoformat(fin_prevu)
            duration = fin - debut
            hours = duration.total_seconds() / 3600
            days = hours / 24
            
            # Tarification dégressive selon la durée
            if days >= 30:
                total_cost += (days / 30) * infra["prix_mois"]
            elif days >= 7:
                total_cost += (days / 7) * infra["prix_semaine"]
            else:
                total_cost += days * infra["prix_jour"]

    # Ajout du coût d'avitaillement
    if avitaillement_id:
        avitaillement = db.select("Avitaillement", filters={"Id": avitaillement_id})
        if avitaillement:
            total_cost += avitaillement[0]["cout"]

    return total_cost


def validate_creneau_time_slot(db: DatabaseManager, infrastructure_id: int, 
                               debut_prevu: str, fin_prevu: str,
                               exclude_creneau_id: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """
    ⭐ RÈGLE MÉTIER PRINCIPALE ⭐
    Valide qu'un créneau respecte l'intervalle de sécurité de 90 minutes.
    Cette fonction est au cœur de la logique métier de l'aérodrome.
    
    Args:
        db: Database manager instance
        infrastructure_id: ID de l'infrastructure
        debut_prevu: Début du créneau (format ISO)
        fin_prevu: Fin du créneau (format ISO)
        exclude_creneau_id: ID à exclure lors des mises à jour
        
    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    debut = datetime.fromisoformat(debut_prevu)
    fin = datetime.fromisoformat(fin_prevu)
    
    # Valider que la fin est après le début
    if fin <= debut:
        return False, "End time must be after start time"
    
    # Récupérer tous les créneaux pour cette infrastructure
    all_creneaux = db.select("Creneaux", filters={"infrastructure_id": infrastructure_id})
    
    for existing_creneau in all_creneaux:
        # Ignorer le créneau en cours de mise à jour
        if exclude_creneau_id and existing_creneau["Id"] == exclude_creneau_id:
            continue
            
        existing_debut = datetime.fromisoformat(existing_creneau["debut_prevu"])
        existing_fin = datetime.fromisoformat(existing_creneau["fin_prevu"])
        
        # ⭐ RÈGLE DES 90 MINUTES ⭐
        # Vérifier qu'il y a au moins 90 minutes entre les créneaux
        if (debut < existing_fin + timedelta(minutes=90)) and (fin > existing_debut - timedelta(minutes=90)):
            return False, "Time slot conflicts with an existing one (including 90-minute security interval)"
    
    return True, None


def validate_creneau_state_transition(current_state: str, new_state: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a state transition is allowed based on business rules.
    
    Valid transitions:
    - Demandé -> Confirmé, Annulé
    - Confirmé -> Autorisé, Annulé
    - Autorisé -> Achevé
    - Achevé -> (no transitions)
    - Annulé -> (no transitions)
    
    Args:
        current_state: Current creneau state
        new_state: Desired new state
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    valid_transitions = {
        "Demandé": ["Confirmé", "Annulé"],
        "Confirmé": ["Autorisé", "Annulé"],
        "Autorisé": ["Achevé"],
        "Achevé": [],
        "Annulé": []
    }
    
    # If state hasn't changed, it's valid
    if new_state == current_state:
        return True, None
    
    # Check if transition is allowed
    if new_state not in valid_transitions.get(current_state, []):
        return False, f"Invalid state transition from {current_state} to {new_state}"
    
    return True, None


def get_user_avions(db: DatabaseManager, pilote_id: int) -> List[Dict[str, Any]]:
    """
    Get all avions belonging to a specific pilot.
    
    Args:
        db: Database manager instance
        pilote_id: ID of the pilot
        
    Returns:
        List of avion records
    """
    return db.select("Avion", filters={"pilote_id": pilote_id})


def get_user_creneaux(db: DatabaseManager, pilote_id: int) -> List[Dict[str, Any]]:
    """
    Get all creneaux for a specific pilot.
    
    Args:
        db: Database manager instance
        pilote_id: ID of the pilot
        
    Returns:
        List of creneau records
    """
    return db.select("Creneaux", filters={"pilote_id": pilote_id})


def check_user_owns_avion(db: DatabaseManager, pilote_id: int, immatriculation: str) -> bool:
    """
    Check if a pilot owns a specific avion.
    
    Args:
        db: Database manager instance
        pilote_id: ID of the pilot
        immatriculation: Aircraft registration number
        
    Returns:
        True if the pilot owns the avion, False otherwise
    """
    avion = db.select("Avion", filters={"Immatriculation": immatriculation})
    if not avion:
        return False
    return avion[0].get("pilote_id") == pilote_id


def check_user_owns_creneau(db: DatabaseManager, pilote_id: int, creneau_id: int) -> bool:
    """
    Check if a pilot owns a specific creneau.
    
    Args:
        db: Database manager instance
        pilote_id: ID of the pilot
        creneau_id: ID of the creneau
        
    Returns:
        True if the pilot owns the creneau, False otherwise
    """
    creneau = db.select("Creneaux", filters={"Id": creneau_id})
    if not creneau:
        return False
    return creneau[0].get("pilote_id") == pilote_id


def check_user_access_to_facture(db: DatabaseManager, pilote_id: int, facture_id: int) -> bool:
    """
    Check if a pilot has access to a specific facture (via their creneaux).
    
    Args:
        db: Database manager instance
        pilote_id: ID of the pilot
        facture_id: ID of the facture
        
    Returns:
        True if the pilot has access to the facture, False otherwise
    """
    creneaux = db.select("Creneaux", filters={"facture_id": facture_id, "pilote_id": pilote_id})
    return len(creneaux) > 0


def check_user_access_to_message(db: DatabaseManager, user_id: int, message_id: int) -> bool:
    """
    Check if a user has access to a specific message (as sender or recipient).
    
    Args:
        db: Database manager instance
        user_id: ID of the user
        message_id: ID of the message
        
    Returns:
        True if the user has access to the message, False otherwise
    """
    message = db.select("Messagerie", filters={"Id": message_id})
    if not message:
        return False
    
    msg = message[0]
    return user_id == msg.get("pilote_id") or user_id == msg.get("agent_id")
