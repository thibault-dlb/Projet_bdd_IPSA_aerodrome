#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from passlib.context import CryptContext

# Initialiser le contexte pour le hachage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def populate_database(db_path):
    """Remplit la base de données avec des données de démo."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Table: Carburant ---
        carburants = [
            ('AVGAS 100LL', 2.85),
            ('JET A-1', 1.95),
            ('MOGAS', 2.10)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Carburant (Nom, prix_par_l) VALUES (?, ?)", carburants)

        # --- Table: Infrastructure ---
        infrastructures = [
            (1, 'Hangar H1-A', 'Hangar', 1, 150.0, 900.0, 3200.0),
            (2, 'Parking P1-Nord', 'Parking', 1, 50.0, 300.0, 1000.0),
            (3, 'Parking P2-Sud', 'Parking', 1, 50.0, 300.0, 1000.0),
            (4, 'Hangar H2-B', 'Hangar', 1, 200.0, 1200.0, 4500.0),
            (5, 'Zone de maintenance M1', 'Maintenance', 1, 500.0, 3000.0, 10000.0)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Infrastructure (Id, nom, type, capacite_max, prix_jour, prix_semaine, prix_mois) VALUES (?, ?, ?, ?, ?, ?, ?)", infrastructures)

        # --- Table: Gestionnaire ---
        gestionnaires = [
            (1, 'Dupont', 'Jean', '0102030405', 'jean.dupont@airport.com', 'jdupont', pwd_context.hash('password123')),
            (2, 'Martin', 'Sophie', '0607080910', 'sophie.martin@airport.com', 'smartin', pwd_context.hash('azerty456')),
            (3, 'Tripier de Laubrière', 'Thibault', '0769145620', 'thibdelaub@outlook.fr', 'thibault.dlb', pwd_context.hash('Epicier1'))
        ]
        cursor.executemany("INSERT OR IGNORE INTO Gestionnaire (Id, nom, prenom, tel, mail, username, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)", gestionnaires)

        # --- Table: Pilote ---
        pilotes = [
            (1, 'Durand', 'Pierre', '0611223344', 'p.durand@pilot.com', 'pdurand', 'ATPL-123', 'Class 1-2027', pwd_context.hash('pilotpass1')),
            (2, 'Lefevre', 'Marie', '0655667788', 'm.lefevre@pilot.com', 'mlefevre', 'CPL-456', 'Class 1-2028', pwd_context.hash('pilotpass2')),
            (3, 'Bernard', 'Luc', '0688776655', 'l.bernard@pilot.com', 'lbernard', 'PPL-789', 'Class 2-2026', pwd_context.hash('pilotpass3')),
        ]
        cursor.executemany("INSERT OR IGNORE INTO Pilote (Id, nom, prenom, tel, mail, username, license, medical, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", pilotes)

        # --- Table: Agent d'exploitation ---
        agents = [
            (1, 'Petit', 'Thomas', '0712345678', 't.petit@airport.com', 'tpetit', pwd_context.hash('agentpass1')),
            (2, 'Robert', 'Alice', '0787654321', 'a.robert@airport.com', 'arobert', pwd_context.hash('agentpass2')),
        ]
        cursor.executemany("INSERT OR IGNORE INTO Agent_d_exploitation (Id, nom, prenom, tel, mail, username, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)", agents)

        # --- Table: Avion ---
        avions = [
            ('F-GHTY', 'Cessna', '172 Skyhawk', '7.2m', '1111kg', 'AVGAS 100LL', 1),
            ('F-BPLN', 'Piper', 'PA-28 Archer', '8.2m', '1157kg', 'AVGAS 100LL', 2),
            ('F-WXYZ', 'Robin', 'DR400', '8.72m', '1100kg', 'AVGAS 100LL', 3),
            ('F-ABCD', 'Daher', 'TBM 940', '10.6m', '3353kg', 'JET A-1', 1),
        ]
        cursor.executemany("INSERT OR IGNORE INTO Avion (Immatriculation, marque, modele, dimension, poids, carburant_id, pilote_id) VALUES (?, ?, ?, ?, ?, ?, ?)", avions)

        # --- Table: Avitaillement ---
        avitaillements = [
            (1, '2026-01-10', '14:30', 120.5, 343.42, 'F-GHTY'),
            (2, '2026-01-11', '09:00', 350.0, 682.50, 'F-ABCD'),
            (3, '2026-01-12', '18:00', 95.0, 270.75, 'F-BPLN')
        ]
        cursor.executemany("INSERT OR IGNORE INTO Avitaillement (Id, date, heure, quantite_en_l, cout, avion_id) VALUES (?, ?, ?, ?, ?, ?)", avitaillements)

        # --- Table: Facture ---
        factures = [
            (1, 'FR7630001007941234567890185', '2026-01-15', 1),
            (2, 'FR7630001007941234567890186', '2026-01-16', 2)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Facture (Id, rib, date_d_emission, agent_id) VALUES (?, ?, ?, ?)", factures)

        # --- Table: Creneaux ---
        creneaux = [
            (1, '2026-01-10 14:00', '2026-01-10 15:00', '2026-01-10 14:05', '2026-01-10 14:55', 'Terminé', 343.42 + 50, 1, 1, 2, 1),
            (2, '2026-01-11 08:30', '2026-01-11 10:00', '2026-01-11 08:45', '2026-01-11 09:50', 'Terminé', 682.50 + 150, 2, 1, 1, 2),
            (3, '2026-01-20 10:00', '2026-01-20 12:00', None, None, 'Planifié', None, None, 2, 3, None)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Creneaux (Id, debut_prevu, fin_prevu, debut_reel, fin_reel, etat, cout_total, avitaillement_id, pilote_id, infrastructure_id, facture_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", creneaux)
        
        # --- Table: Messagerie ---
        messages = [
            (1, '2026-01-09', '11:25', 'Bonjour, je confirme ma réservation pour le 10.', 1, 1, 1),
            (2, '2026-01-09', '11:30', 'Bien reçu, votre hangar est réservé.', 0, 1, 1)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Messagerie (Id, date, heure, contenu, sens_d_envoie, agent_id, pilote_id) VALUES (?, ?, ?, ?, ?, ?, ?)", messages)


        conn.commit()
        print("Base de données remplie avec succès.")

    except sqlite3.Error as e:
        print(f"Erreur SQLite lors du remplissage : {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    populate_database("Code_SQlite.db")
