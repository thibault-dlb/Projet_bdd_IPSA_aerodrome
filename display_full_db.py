#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def display_full_database(db_path):
    """
    Affiche la structure et le contenu complet d'une base de données SQLite.
    """
    if not os.path.exists(db_path):
        print(f"Erreur : Le fichier de base de données '{db_path}' n'a pas été trouvé.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"=== Analyse complète de la base de données : {os.path.basename(db_path)} ===")

        # Obtenir la liste de toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("\nLa base de données est vide (aucune table trouvée).")
            return

        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            if table_name.startswith('sqlite_'):
                continue
            
            print(f"\n\n\n### Table : {table_name} ###")
            print("-" * (14 + len(table_name)))

            # 1. Afficher la structure (schéma)
            print("\n[...Structure...]")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            print(f"  {'Nom de la colonne':<25} {'Type':<15} {'Non Nul':<10} {'Clé Primaire':<15}")
            print(f"  {'-'*25:<25} {'-'*15:<15} {'-'*10:<10} {'-'*15:<15}")
            for col in columns_info:
                is_not_null = "Oui" if col[3] else "Non"
                is_pk = "Oui" if col[5] else "Non"
                print(f"  {col[1]:<25} {col[2]:<15} {is_not_null:<10} {is_pk:<15}")

            # 2. Afficher le contenu
            print("\n[...Contenu...]")
            cursor.execute(f"SELECT * FROM {table_name}")
            
            # Obtenir les noms des colonnes pour l'affichage du contenu
            column_names = [description[0] for description in cursor.description]
            print(" | ".join(column_names))
            print("-+-".join(['-' * len(name) for name in column_names]))

            rows = cursor.fetchall()
            if not rows:
                print("(Cette table est vide)")
            else:
                for row in rows:
                    # Convertir chaque élément de la ligne en chaîne de caractères pour l'affichage
                    print(" | ".join(map(str, row)))

    except sqlite3.Error as e:
        print(f"\nErreur SQLite : {e}")

    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    display_full_database("Code_SQlite.db")
