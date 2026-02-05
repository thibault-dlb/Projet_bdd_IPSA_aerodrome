import sqlite3
from pathlib import Path

DATABASE_URL = "Code_SQlite.db"

def create_database_schema(db_path: str):
    """
    Crée le schéma de la base de données SQLite avec toutes les tables.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Activer le support des clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Table Carburant
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Carburant (
                Nom TEXT PRIMARY KEY NOT NULL,
                prix_par_l REAL NOT NULL
            );
        """)

        # Table Infrastructure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Infrastructure (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL,
                capacite_max INTEGER NOT NULL,
                prix_jour REAL NOT NULL,
                prix_semaine REAL NOT NULL,
                prix_mois REAL NOT NULL
            );
        """)

        # Table Gestionnaire
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Gestionnaire (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
        """)

        # Table Pilote
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Pilote (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                license TEXT NOT NULL,
                medical TEXT NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)

        # Table Agent_d_exploitation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Agent_d_exploitation (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
        """)

        # Table Avion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Avion (
                Immatriculation TEXT PRIMARY KEY NOT NULL,
                marque TEXT NOT NULL,
                modele TEXT NOT NULL,
                dimension TEXT NOT NULL,
                poids TEXT NOT NULL,
                carburant_id TEXT,
                pilote_id INTEGER,
                FOREIGN KEY (carburant_id) REFERENCES Carburant(Nom) ON DELETE SET NULL,
                FOREIGN KEY (pilote_id) REFERENCES Pilote(Id) ON DELETE CASCADE
            );
        """)

        # Table Avitaillement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Avitaillement (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                heure TEXT NOT NULL,
                quantite_en_l REAL NOT NULL,
                cout REAL NOT NULL,
                avion_id TEXT NOT NULL,
                FOREIGN KEY (avion_id) REFERENCES Avion(Immatriculation) ON DELETE CASCADE
            );
        """)



        # Table Creneaux
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Creneaux (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                debut_prevu TEXT NOT NULL,
                fin_prevu TEXT NOT NULL,
                avion_id TEXT,
                debut_reel TEXT,
                fin_reel TEXT,
                etat TEXT NOT NULL,
                cout_total REAL,
                avitaillement_id INTEGER,
                pilote_id INTEGER,
                infrastructure_id INTEGER,
                FOREIGN KEY (avion_id) REFERENCES Avion(Immatriculation) ON DELETE SET NULL,
                FOREIGN KEY (avitaillement_id) REFERENCES Avitaillement(Id) ON DELETE SET NULL,
                FOREIGN KEY (pilote_id) REFERENCES Pilote(Id) ON DELETE CASCADE,
                FOREIGN KEY (infrastructure_id) REFERENCES Infrastructure(Id) ON DELETE SET NULL
            );
        """)

        # Table Messagerie
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messagerie (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                heure TEXT NOT NULL,
                contenu TEXT NOT NULL,
                sens_d_envoie INTEGER NOT NULL,
                agent_id INTEGER,
                pilote_id INTEGER,
                FOREIGN KEY (agent_id) REFERENCES Agent_d_exploitation(Id) ON DELETE SET NULL,
                FOREIGN KEY (pilote_id) REFERENCES Pilote(Id) ON DELETE SET NULL
            );
        """)

        conn.commit()
        print(f"Schéma de la base de données créé avec succès dans {db_path}")

    except sqlite3.Error as e:
        print(f"Erreur lors de la création du schéma de la base de données : {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Supprime l'ancienne base de données si elle existe pour s'assurer d'une nouvelle création
    db_file = Path(DATABASE_URL)
    if db_file.exists():
        print(f"Suppression de l'ancienne base de données : {db_file}")
        db_file.unlink()

    create_database_schema(DATABASE_URL)