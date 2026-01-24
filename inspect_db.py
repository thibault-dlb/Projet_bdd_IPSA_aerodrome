#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def inspect_sqlite_database(db_path):
    """
    Se connecte à une base de données SQLite et affiche sa structure
    (tables et colonnes).

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

        print(f"--- Structure de la base de données : {os.path.basename(db_path)} ---")

        # Obtenir la liste des tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("\nLa base de données est vide (aucune table trouvée).")
            return

        # Pour chaque table, obtenir son schéma
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            # Ignorer les tables internes de sqlite
            if table_name.startswith('sqlite_'):
                continue
            
            print(f"\n\n-> Table : {table_name}")
            print("-" * (12 + len(table_name)))

            # Utiliser PRAGMA pour obtenir les informations de la table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Afficher les en-têtes des colonnes
            print(f"  {'Nom de la colonne':<25} {'Type':<15} {'Non Nul':<10} {'Clé Primaire':<15}")
            print(f"  {'-'*25:<25} {'-'*15:<15} {'-'*10:<10} {'-'*15:<15}")

            # Afficher les détails de chaque colonne
            for col in columns:
                # col est un tuple: (cid, name, type, notnull, dflt_value, pk)
                col_name = col[1]
                col_type = col[2]
                is_not_null = "Oui" if col[3] else "Non"
                is_pk = "Oui" if col[5] else "Non"
                print(f"  {col_name:<25} {col_type:<15} {is_not_null:<10} {is_pk:<15}")

    except sqlite3.Error as e:
        print(f"\nErreur SQLite : {e}")
        print(f"Le fichier '{db_path}' n'est peut-être pas un fichier de base de données SQLite valide.")

    finally:
        # S'assurer de fermer la connexion
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    # Chemin vers votre base de données
    database_file = "/home/thibault_dlb/Code_SQlite.db"
    inspect_sqlite_database(database_file)
