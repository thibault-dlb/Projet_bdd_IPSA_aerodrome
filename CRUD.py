#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path
from typing import Any, List, Dict, Optional

class DatabaseManager:
    """
    Une classe pour gérer toutes les opérations CRUD sur la base de données SQLite de l'aéroport.
    """
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de base de données.

        Args:
            db_path (str): Le chemin vers le fichier de la base de données SQLite.
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"La base de données n'a pas été trouvée à l'emplacement : {self.db_path}")

    def _create_connection(self):
        """Crée et retourne une connexion à la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Activer le support des clés étrangères
            conn.execute("PRAGMA foreign_keys = ON;")
            # Retourner les lignes comme des dictionnaires
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données: {e}")
            return None

    # ------------------------------------------- 
    # 1. Fonctions CRUD Génériques
    # ------------------------------------------- 

    def create(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Crée une nouvelle ligne dans une table.

        Args:
            table (str): Le nom de la table.
            data (Dict[str, Any]): Un dictionnaire {colonne: valeur}.

        Returns:
            Optional[int]: L'ID de la nouvelle ligne insérée, ou None en cas d'erreur.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self._create_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, list(data.values()))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                print(f"Erreur d'intégrité lors de la création : {e}")
                conn.rollback()
            except sqlite3.Error as e:
                print(f"Erreur lors de la création : {e}")
                conn.rollback()
        return None

    def select(self, table: str, filters: Dict[str, Any] = None, columns: List[str] = None, join: str = None) -> List[Dict[str, Any]]:
        """
        Sélectionne des lignes dans une table avec des filtres optionnels.

        Args:
            table (str): Le nom de la table principale.
            filters (Dict[str, Any], optional): Dictionnaire de filtres {colonne: valeur}.
            columns (List[str], optional): Liste des colonnes à retourner. Par défaut, toutes (*).
            join (str, optional): Clause JOIN complète (ex: "JOIN Pilote ON Avion.pilote_id = Pilote.Id").

        Returns:
            List[Dict[str, Any]]: Une liste de dictionnaires représentant les lignes trouvées.
        """
        cols = ', '.join(columns) if columns else '*'
        sql = f"SELECT {cols} FROM {table}"
        
        if join:
            sql += f" {join}"

        values = []
        if filters:
            conditions = " AND ".join([f"{key} = ?" for key in filters.keys()])
            sql += f" WHERE {conditions}"
            values = list(filters.values())

        with self._create_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                rows = cursor.fetchall()
                # Convertir les objets sqlite3.Row en dictionnaires
                return [dict(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erreur lors de la sélection : {e}")
        return []

    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> int:
        """
        Met à jour une ou plusieurs lignes dans une table.

        Args:
            table (str): Le nom de la table.
            data (Dict[str, Any]): Dictionnaire des nouvelles données {colonne: nouvelle_valeur}.
            filters (Dict[str, Any]): Dictionnaire de filtres {colonne: valeur} pour la clause WHERE.

        Returns:
            int: Le nombre de lignes affectées.
        """
        set_placeholders = ', '.join([f"{key} = ?" for key in data.keys()])
        where_placeholders = " AND ".join([f"{key} = ?" for key in filters.keys()])
        sql = f"UPDATE {table} SET {set_placeholders} WHERE {where_placeholders}"
        
        values = list(data.values()) + list(filters.values())
        
        with self._create_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
                return cursor.rowcount
            except sqlite3.Error as e:
                print(f"Erreur lors de la mise à jour : {e}")
                conn.rollback()
        return 0

    def delete(self, table: str, filters: Dict[str, Any]) -> int:
        """
        Supprime une ou plusieurs lignes d'une table.

        Args:
            table (str): Le nom de la table.
            filters (Dict[str, Any]): Dictionnaire de filtres {colonne: valeur} pour la clause WHERE.

        Returns:
            int: Le nombre de lignes supprimées.
        """
        where_placeholders = " AND ".join([f"{key} = ?" for key in filters.keys()])
        sql = f"DELETE FROM {table} WHERE {where_placeholders}"
        
        with self._create_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, list(filters.values()))
                conn.commit()
                return cursor.rowcount
            except sqlite3.IntegrityError as e:
                print(f"Erreur d'intégrité : impossible de supprimer car l'enregistrement est lié à d'autres données. Détails: {e}")
                conn.rollback()
            except sqlite3.Error as e:
                print(f"Erreur lors de la suppression : {e}")
                conn.rollback()
        return 0

    def upsert(self, table: str, data: Dict[str, Any], unique_key: Dict[str, Any]) -> Optional[int]:
        """
        Met à jour une ligne si elle existe (basé sur unique_key), sinon la crée (UPSERT).

        Args:
            table (str): Le nom de la table.
            data (Dict[str, Any]): Les données à insérer ou à mettre à jour.
            unique_key (Dict[str, Any]): Le filtre pour trouver la ligne existante.

        Returns:
            Optional[int]: L'ID de la ligne affectée ou None en cas d'erreur.
        """
        existing = self.select(table, filters=unique_key)
        if existing:
            # La ligne existe, on la met à jour
            rows_affected = self.update(table, data, unique_key)
            return existing[0]['Id'] if rows_affected > 0 and 'Id' in existing[0] else None
        else:
            # La ligne n'existe pas, on la crée
            full_data = {**unique_key, **data}
            return self.create(table, full_data)

    # ------------------------------------------- 
    # 2. Fonctions Spécifiques Pertinentes
    # ------------------------------------------- 

    def get_user_by_username(self, username: str, user_type: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur (Pilote, Gestionnaire, Agent) par son nom d'utilisateur.
        
        Args:
            username (str): Le nom d'utilisateur.
            user_type (str): Le type d'utilisateur ('Pilote', 'Gestionnaire', 'Agent_d_exploitation').
        """
        if user_type not in ['Pilote', 'Gestionnaire', 'Agent_d_exploitation']:
            print("Type d'utilisateur invalide.")
            return None
        
        results = self.select(user_type, filters={'username': username})
        return results[0] if results else None

    def get_avions_for_pilote(self, pilote_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les avions associés à un pilote."""
        return self.select('Avion', filters={'pilote_id': pilote_id})

    def get_creneaux_for_pilote(self, pilote_id: int, upcoming_only: bool = False) -> List[Dict[str, Any]]:
        """Récupère les créneaux de vol pour un pilote."""
        filters = {'pilote_id': pilote_id}
        if upcoming_only:
            filters['etat'] = 'Planifié'
        return self.select('Creneaux', filters=filters)

    def get_full_creneau_details(self, creneau_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails complets d'un créneau en utilisant des jointures.
        """
        sql = """
            SELECT
                c.Id as creneau_id, c.etat, c.debut_prevu, c.fin_prevu,
                p.nom as pilote_nom, p.prenom as pilote_prenom,
                a.Immatriculation as avion_immat, a.modele as avion_modele,
                i.nom as infra_nom, i.type as infra_type,
                f.Id as facture_id, f.date_d_emission
            FROM Creneaux c
            LEFT JOIN Pilote p ON c.pilote_id = p.Id
            LEFT JOIN Avion a ON p.Id = a.pilote_id
            LEFT JOIN Infrastructure i ON c.infrastructure_id = i.Id
            LEFT JOIN Facture f ON c.facture_id = f.Id
            WHERE c.Id = ?
        """
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (creneau_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_creneau_status(self, creneau_id: int, new_status: str) -> int:
        """Met à jour le statut d'un créneau (ex: 'Planifié' -> 'Terminé')."""
        return self.update('Creneaux', data={'etat': new_status}, filters={'Id': creneau_id})

    def get_invoices_for_pilote(self, pilote_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les factures d'un pilote via les créneaux."""
        join_clause = """
        JOIN Creneaux ON Facture.Id = Creneaux.facture_id
        """
        return self.select('Facture', filters={'Creneaux.pilote_id': pilote_id}, join=join_clause)


if __name__ == '__main__':
    # --- Démonstration de l'utilisation de la classe ---
    
    db_manager = DatabaseManager('Code_SQlite.db')

    print("--- 1. Test de la fonction SELECT ---")
    pilotes = db_manager.select('Pilote')
    print(f"Nombre de pilotes trouvés : {len(pilotes)}")
    if pilotes:
        print(f"Premier pilote : {pilotes[0]['prenom']} {pilotes[0]['nom']}")

    print("\n--- 2. Test de la fonction CREATE ---")
    new_pilote_data = {
        'nom': 'Skywalker',
        'prenom': 'Luke',
        'tel': '0601020304',
        'mail': 'luke@rebellion.com',
        'username': 'lskywalker',
        'license': 'PPL-REBEL-01',
        'medical': 'Class 1',
        'password_hash': 'hashed_password'
    }
    new_id = db_manager.create('Pilote', new_pilote_data)
    if new_id:
        print(f"Nouveau pilote 'Luke Skywalker' créé avec l'ID : {new_id}")
    else:
        print("Échec de la création du pilote.")

    print("\n--- 3. Test de la fonction UPDATE ---")
    if new_id:
        rows_affected = db_manager.update('Pilote', data={'tel': '0987654321'}, filters={'Id': new_id})
        if rows_affected > 0:
            updated_pilote = db_manager.select('Pilote', filters={'Id': new_id})[0]
            print(f"Numéro de téléphone de Luke mis à jour : {updated_pilote['tel']}")
    
    print("\n--- 4. Test de la fonction UPSERT ---")
    # Cas 1: Mise à jour d'un carburant existant
    db_manager.upsert('Carburant', data={'prix_par_l': 3.05}, unique_key={'Nom': 'AVGAS 100LL'})
    updated_fuel = db_manager.select('Carburant', filters={'Nom': 'AVGAS 100LL'})[0]
    print(f"Prix de l'AVGAS 100LL mis à jour à : {updated_fuel['prix_par_l']}")
    # Cas 2: Création d'un nouveau carburant
    new_fuel_id = db_manager.upsert('Carburant', data={'prix_par_l': 5.50}, unique_key={'Nom': 'Kérosène de l\'Etoile Noire'})
    print(f"Nouveau carburant créé avec l'ID (via set) : {new_fuel_id}")


    print("\n--- 5. Test des fonctions spécifiques ---")
    pilote_pierre = db_manager.get_user_by_username('pdurand', 'Pilote')
    if pilote_pierre:
        print(f"Recherche de l'utilisateur 'pdurand' réussie. ID: {pilote_pierre['Id']}")
        avions_pierre = db_manager.get_avions_for_pilote(pilote_pierre['Id'])
        print(f"Pierre Durand a {len(avions_pierre)} avion(s). Immatriculation: {avions_pierre[0]['Immatriculation']}")

    print("\n--- 6. Test d'une fonction avec JOIN ---")
    creneau_details = db_manager.get_full_creneau_details(1)
    if creneau_details:
        print("Détails complets pour le créneau ID 1:")
        for key, value in creneau_details.items():
            print(f"  - {key}: {value}")

    print("\n--- 7. Test de la fonction DELETE ---")
    if new_id:
        rows_deleted = db_manager.delete('Pilote', filters={'Id': new_id})
        if rows_deleted > 0:
            print(f"Le pilote 'Luke Skywalker' (ID: {new_id}) a été supprimé avec succès.")
    
    # Nettoyage du carburant ajouté
    db_manager.delete('Carburant', filters={'Nom': "Kérosène de l\'Etoile Noire"})
    print("Carburant de test supprimé.")
    # Reset du prix du carburant modifié
    db_manager.update('Carburant', data={'prix_par_l': 2.85}, filters={'Nom': 'AVGAS 100LL'})
    print("Prix du carburant initial restauré.")
