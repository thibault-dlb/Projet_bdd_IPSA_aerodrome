#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import argparse # Import argparse

def inspect_sqlite_database(db_path, table_name=None, data_filter=None): # Add parameters
    """
    Se connecte à une base de données SQLite et affiche sa structure
    (tables et colonnes) ou les données d'une table spécifique.

    Args:
        db_path (str): Le chemin vers le fichier de la base de données SQLite.
        table_name (str, optional): Le nom de la table dont les données doivent être affichées.
        data_filter (str, optional): Une clause WHERE pour filtrer les données (ex: "id = 1").
    """
    if not os.path.exists(db_path):
        print(f"Erreur : Le fichier de base de données '{db_path}' n'a pas été trouvé.")
        return

    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"--- Opération sur la base de données : {os.path.basename(db_path)} ---")

        if table_name and data_filter:
            # Display data for a specific table with a filter
            query = f"SELECT * FROM {table_name} WHERE {data_filter}"
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                print(f"\nAucune donnée trouvée dans la table '{table_name}' avec le filtre '{data_filter}'.")
                return

            # Get column names
            col_names = [description[0] for description in cursor.description]
            print(f"\nDonnées de la table '{table_name}' (filtre: '{data_filter}') :")
            print("-" * (len(query) + 20)) # A simple separator

            # Print header
            print(" | ".join(col_names))
            print(" | ".join(['-' * len(col) for col in col_names]))

            # Print rows
            for row in rows:
                print(" | ".join(map(str, row)))

        elif table_name: # If only table_name is provided, show all data in that table
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                print(f"\nAucune donnée trouvée dans la table '{table_name}'.")
                return

            # Get column names
            col_names = [description[0] for description in cursor.description]
            print(f"\nDonnées de la table '{table_name}' :")
            print("-" * (len(query) + 20)) # A simple separator

            # Print header
            print(" | ".join(col_names))
            print(" | ".join(['-' * len(col) for col in col_names]))

            # Print rows
            for row in rows:
                print(" | ".join(map(str, row)))

        else:
            # Original functionality: display all tables and their schema
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
    except Exception as e:
        print(f"\nUne erreur inattendue est survenue : {e}")

    finally:
        # S'assurer de fermer la connexion
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspecte la structure d'une base de données SQLite ou affiche les données d'une table.")
    parser.add_argument("--db", default="Code_SQlite.db", help="Chemin vers le fichier de la base de données SQLite.")
    parser.add_argument("--table", help="Nom de la table à inspecter (pour le schéma ou les données).")
    parser.add_argument("--filter", help="Clause WHERE pour filtrer les données de la table (ex: 'Id = 1'). Nécessite --table.")
    
    args = parser.parse_args()

    if args.filter and not args.table:
        parser.error("--filter nécessite --table pour être spécifié.")

    inspect_sqlite_database(args.db, args.table, args.filter)