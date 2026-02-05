-- Database Schema Export for DB-Main
-- Generated from Code_SQlite.db
-- Tables ordered by dependency (referenced tables first)

-- Tables without dependencies
CREATE TABLE Carburant (
                Nom TEXT PRIMARY KEY NOT NULL,
                prix_par_l REAL NOT NULL
            );

CREATE TABLE Pilote (
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

CREATE TABLE Agent_d_exploitation (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );

CREATE TABLE Gestionnaire (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );

CREATE TABLE Infrastructure (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL,
                capacite_max INTEGER NOT NULL,
                prix_jour REAL NOT NULL,
                prix_semaine REAL NOT NULL,
                prix_mois REAL NOT NULL
            );

-- Tables with one level of dependencies
CREATE TABLE Avion (
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

CREATE TABLE Messagerie (
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

-- Tables with two levels of dependencies
CREATE TABLE Avitaillement (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                heure TEXT NOT NULL,
                quantite_en_l REAL NOT NULL,
                cout REAL NOT NULL,
                avion_id TEXT NOT NULL,
                FOREIGN KEY (avion_id) REFERENCES Avion(Immatriculation) ON DELETE CASCADE
            );

-- Tables with three levels of dependencies
CREATE TABLE Creneaux (
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

