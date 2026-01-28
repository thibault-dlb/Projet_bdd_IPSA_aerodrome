# ✈️ Dossier de Spécifications : Système de Gestion d'Aérodrome

Ce document détaille la conception du système d'information pour la gestion des mouvements, des services au sol et de la facturation d'un aérodrome régional privé[cite: 2].

---

## 🛠️ Architecture Technique
* **Langage :** Python.
* **Framework API :** FastAPI.
* **Base de Données :** SQLite (`Code_SQlite.db`).
* **Architecture :** API REST.

---

## 👥 Profils et Privilèges

Le système distingue trois types d'utilisateurs avec des niveaux de droits d'accès spécifiques :

| Rôle | Niveau de Privilège | Description |
| :--- | :---: | :--- |
| **Gestionnaire** | **0** (Maximum) | Supervise l'infrastructure, les revenus et génère les rapports. |
| **Agent d'Exploitation** | **1** | Gère les opérations, valide les créneaux et s'occupe de la facturation. |
| **Pilote / Propriétaire** | **2** (Minimum) | Gère son compte, ses aéronefs et demande des services ou créneaux. |

---

## 🗄️ Structure de la Base de Données (MLD)

Organisation des données basée sur le schéma SQLite de l'aérodrome :

### 1. Utilisateurs et RH
* **Pilote** : Identité, licence, aptitude médicale et hash du mot de passe.
* **Agent_d_exploitation** : Personnel gérant les flux et factures.
* **Gestionnaire** : Accès aux statistiques et à la gestion des infrastructures.

### 2. Assets et Infrastructures
* **Avion** : Lié à un **Pilote** et associé à un type de **Carburant**.
* **Infrastructure** : Pistes, hangars ou parkings avec tarifs dégressifs.
* **Carburant** : Référence les prix au litre pour l'AVGAS 100LL et le JET A1.

### 3. Opérations et Logistique
* **Creneaux** : Table pivot reliant le mouvement, l'avion, l'infrastructure occupée et la facture.
* **Avitaillement** : Enregistre les prises de carburant (quantité, date, coût) liées à un avion.
* **Messagerie** : Supporte les échanges bidirectionnels entre Pilotes et Agents.

---

## 📋 Règles Métier Impératives

### 1. Gestion des Mouvements (Créneaux)
* **Intervalle de sécurité** : Un créneau doit respecter un intervalle minimum de **90 minutes** entre deux mouvements.
* **Cycle de vie** : Le champ `etat` doit refléter les étapes suivantes : *Demandé, Confirmé, Autorisé, Achevé, Annulé*.
* **Indisponibilité** : Dès réservation, le créneau est verrouillé pour les autres aéronefs.

### 2. Services au Sol
* **Occupation** : Les hangars ont une capacité limitée qui doit être vérifiée avant toute affectation.
* **Facturation Carburant** : Calculée au litre selon le type d'appareil (AVGAS 100LL ou JET A1).

### 3. Facturation & Reporting
* **Consolidation** : Une facture regroupe l'intégralité des services d'un même mouvement aérien.
* **Reporting** : Visualisation des flux de mouvements (jour/semaine/mois) et des revenus.

---

## 🚀 Plan d'Action (Checklist)

### 🔹 Backend (FastAPI & Python)
- [ ] **Modèles Pydantic** : Créer les schémas de données pour chaque table SQLite.
- [ ] **Sécurité** : Implémenter le hachage des mots de passe et la vérification des niveaux (0, 1, 2).
- [ ] **Logique Créneaux** : Coder la vérification SQL de l'intervalle des 90 minutes lors d'un `POST`.
- [ ] **Calculateur de Prix** : Fonction automatique agrégeant carburant et infrastructures dans `cout_total`.

### 🔹 Analyse et Livrables
- [ ] **Dictionnaire des données** : Préciser le rôle de chaque colonne et les unités.
- [ ] **MCD / MLD** : Schématiser les relations pour le dossier d'analyse.