# Projet de Gestion d'Aéroport

Ce projet est une application web simple pour la gestion d'un aéroport, développée avec un backend en Python (FastAPI) et un frontend en HTML, CSS et JavaScript pur.

## Structure du Projet

- `api/`: Contient le code de l'API backend.
  - `main.py`: Le point d'entrée de l'API FastAPI, définissant toutes les routes.
  - `models.py`: Les modèles Pydantic pour la validation des données.
- `index.html`: Le point d'entrée du frontend de l'application.
- `style.css`: La feuille de style pour le frontend.
- `CRUD.py`: Une classe `DatabaseManager` pour gérer toutes les opérations de base de données (Créer, Lire, Mettre à jour, Supprimer).
- `Code_SQlite.db`: La base de données SQLite.
- `requirements.txt`: Les dépendances Python du projet.
- `add_user.py`: Un script pour ajouter manuellement des utilisateurs à la base de données.
- `populate_db.py`: Un script pour remplir la base de données avec des données initiales.
- `display_full_db.py`: Un script pour afficher tout le contenu de la base de données.
- `empty_db.py`: Un script pour vider toutes les tables de la base de données.
- `inspect_db.py`: Un script pour inspecter le schéma de la base de données.

## Prérequis

- Python 3.7+
- Un environnement virtuel (recommandé)

## Installation

1.  Clonez le dépôt :
    ```bash
    git clone <URL_DU_REPO>
    cd <NOM_DU_DOSSIER>
    ```

2.  Créez et activez un environnement virtuel :
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4.  (Optionnel) Remplissez la base de données avec des données de test :
    ```bash
    python populate_db.py
    ```

## Utilisation

### Lancement du Backend

Pour démarrer le serveur API, exécutez la commande suivante à la racine du projet :

```bash
uvicorn api.main:app --reload
```

Le serveur sera accessible à l'adresse `http://127.0.0.1:8000`.

### Accès au Frontend

Ouvrez le fichier `index.html` dans votre navigateur. Vous pouvez utiliser une extension comme "Live Server" dans VS Code pour le servir localement.

L'interface vous permet de vous connecter en tant que :
- **Gestionnaire** (ex: `jleclerc`, mdp: `securepass123`) niveau de privilège 0
- **Agent** (ex: `fhardy`, mdp: `agentpass456`) niveau de privilège 1
- **Pilote** (ex: `pdurand`, mdp: `pilote789`) niveau de privilège 2

Selon le type d'utilisateur, vous aurez différentes options pour créer d'autres comptes.

### Scripts Utilitaires

- **Ajouter un utilisateur :**
  ```bash
  python add_user.py
  ```
- **Afficher la base de données :**
  ```bash
  python display_full_db.py
  ```
- **Vider la base de données :**
  ```bash
  python empty_db.py
  ```

## Fonctionnalités de l'API

L'API expose des points de terminaison CRUD pour les entités suivantes :
- `Carburant`
- `Pilote`
- `Infrastructure`
- `Avion`
- `Creneaux`
- `Gestionnaire`
- `Agent_d_exploitation`
- `Facture`
- `Messagerie`

La documentation complète de l'API (générée par Swagger) est disponible à l'adresse `http://127.0.0.1:8000/docs` lorsque le serveur est en cours d'exécution.
