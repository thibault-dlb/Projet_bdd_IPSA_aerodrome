#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def empty_database(db_path):
    """
    Supprime toutes les données de toutes les tables d'une base de données SQLite.

    Args:
        db_path (str): Le chemin vers le fichier de la base de données SQLite.
    """
    if not os.path.exists(db_path):
        print(f"Erreur : Le fichier de base de données '{db_path}' n'a pas été trouvé.")
        return

    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Désactiver temporairement les contraintes de clé étrangère
        cursor.execute("PRAGMA foreign_keys = OFF;")
        print("Contraintes de clé étrangère désactivées temporairement.")

        # Obtenir la liste de toutes les tables utilisateur
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()

        if not tables:
            print("La base de données ne contient aucune table.")
            return

        print("\nDébut de la suppression des données...")
        
        # Pour chaque table, supprimer toutes les lignes
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            try:
                print(f"  - Vidage de la table : {table_name}")
                cursor.execute(f"DELETE FROM {table_name};")
                # Optionnel : réinitialiser les séquences auto-incrémentées si nécessaire
                # Pour sqlite_sequence, on peut supprimer l'entrée de la table
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name=?", (table_name,))

            except sqlite3.Error as e:
                print(f"    Erreur lors du vidage de la table {table_name}: {e}")

        # Valider les modifications
        conn.commit()
        print("\nToutes les tables ont été vidées avec succès.")

    except sqlite3.Error as e:
        print(f"\nUne erreur SQLite est survenue : {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            print("Transaction annulée.")

    finally:
        # S'assurer de réactiver les clés étrangères et de fermer la connexion
        if 'conn' in locals() and conn:
            try:
                # Réactiver les contraintes de clé étrangère
                cursor.execute("PRAGMA foreign_keys = ON;")
                print("Contraintes de clé étrangère réactivées.")
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erreur lors de la réactivation des clés étrangères : {e}")
            finally:
                conn.close()
                print("Connexion à la base de données fermée.")


if __name__ == "__main__":
    database_file = "Code_SQlite.db"
    
    # Demander une confirmation à l'utilisateur
    confirm = input(f"ATTENTION : Cette action va supprimer définitivement TOUTES les données de la base '{database_file}'.\nÊtes-vous sûr de vouloir continuer ? (oui/non) : ")
    
    if confirm.lower() == 'oui':
        print("\nConfirmation reçue. Lancement du processus...")
        empty_database(database_file)
    else:
        print("\nOpération annulée par l'utilisateur.")
