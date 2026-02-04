# add_user.py

import sys
from pathlib import Path
from getpass import getpass

# Add the parent directory to sys.path to import CRUD.py
sys.path.append(str(Path(__file__).parent.parent))

from CRUD import DatabaseManager
from business import hash_password  # Import the hashing function

DATABASE_URL = "Code_SQlite.db"

def add_user():
    db = DatabaseManager(DATABASE_URL)

    print("Type d'utilisateur à ajouter :")
    print("1. Pilote")
    print("2. Agent d'exploitation")
    print("3. Gestionnaire")
    user_type_choice = input("Entrez votre choix (1, 2 ou 3) : ")

    if user_type_choice == '1':
        table_name = "Pilote"
        print(f"\nAjout d'un {table_name} :")
        nom = input("Nom : ")
        prenom = input("Prénom : ")
        tel = input("Téléphone : ")
        mail = input("Email : ")
        username = input("Nom d'utilisateur : ")
        license = input("Numéro de licence : ")
        medical = input("Certification médicale : ")
        password = getpass("Mot de passe : ")
        password_hash = hash_password(password)

        user_data = {
            "nom": nom,
            "prenom": prenom,
            "tel": tel,
            "mail": mail,
            "username": username,
            "license": license,
            "medical": medical,
            "password_hash": password_hash
        }
    elif user_type_choice == '2':
        table_name = "Agent_d_exploitation"
        print(f"\nAjout d'un {table_name} :")
        nom = input("Nom : ")
        prenom = input("Prénom : ")
        tel = input("Téléphone : ")
        mail = input("Email : ")
        username = input("Nom d'utilisateur : ")
        password = getpass("Mot de passe : ")
        password_hash = hash_password(password)

        user_data = {
            "nom": nom,
            "prenom": prenom,
            "tel": tel,
            "mail": mail,
            "username": username,
            "password_hash": password_hash
        }
    elif user_type_choice == '3':
        table_name = "Gestionnaire"
        print(f"\nAjout d'un {table_name} :")
        nom = input("Nom : ")
        prenom = input("Prénom : ")
        tel = input("Téléphone : ")
        mail = input("Email : ")
        username = input("Nom d'utilisateur : ")
        password = getpass("Mot de passe : ")
        password_hash = hash_password(password)

        user_data = {
            "nom": nom,
            "prenom": prenom,
            "tel": tel,
            "mail": mail,
            "username": username,
            "password_hash": password_hash
        }
    else:
        print("Choix invalide.")
        return

    try:
        new_id = db.create(table_name, data=user_data)
        if new_id:
            print(f"{table_name} '{username}' ajouté avec succès! ID: {new_id}")
        else:
            print(f"Échec de l'ajout du {table_name}. Peut-être que le nom d'utilisateur existe déjà ou données invalides.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'ajout de l'utilisateur : {e}")

if __name__ == "__main__":
    add_user()
