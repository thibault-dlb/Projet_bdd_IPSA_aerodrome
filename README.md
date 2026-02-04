# 🛫 Projet de Gestion d'Aérodrome

**Système de gestion d'aérodrome simplifié pour présentation académique**

## 📋 Vue d'ensemble

Application web permettant la gestion des mouvements aériens, des services au sol et de la facturation pour un aérodrome régional privé.

### Architecture
- **Backend**: FastAPI (Python 3)
- **Base de données**: SQLite
- **Frontend**: HTML/CSS/JavaScript
- **Sécurité**: JWT + bcrypt

## ⭐ Fonctionnalités principales

### 1. Authentification Multi-Rôles
- **3 types d'utilisateurs** avec droits différents:
  - 🔧 **Gestionnaire** (niveau 0) - Accès total, gestion infrastructure
  - 👔 **Agent d'exploitation** (niveau 1) - Validation créneaux, facturation
  - 👨‍✈️ **Pilote** (niveau 2) - Gestion avions, demande de créneaux

### 2. Règle Métier des 90 Minutes ⏱️
Validation automatique garantissant **90 minutes minimum** entre deux mouvements sur une même infrastructure.

**Implémentation**: `business.py` → `validate_creneau_time_slot()`

### 3. Calcul Automatique de Facturation 💰
Calcul du coût total basé sur:
- Location infrastructure (tarif dégressif: jour/semaine/mois)
- Avitaillement en carburant

**Implémentation**: `business.py` → `calculate_creneau_cost()`

### 4. Sécurité 🔐
- Mots de passe hashés avec **bcrypt**
- Authentification par **JWT tokens** (expiration 30 min)
- **RBAC** (Role-Based Access Control)

## 🗂️ Structure du Projet

```
├── api/
│   ├── main.py          # API FastAPI avec endpoints
│   └── models.py        # Modèles Pydantic
├── business.py          # Ensemble des fonctions buisness
├── CRUD.py             # Gestionnaire de base de données
├── create_db.py        # Création du schéma SQLite
├── populate_db.py      # Données de démo
└── *.html              # Interface utilisateur


```

## 🚀 Installation et Lancement

### Prérequis
- Python 3.7+
- pip

### Installation
```bash
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python populate_db.py
```

### Lancement
```bash
# Démarrer l'API
uvicorn api.main:app --reload
```

Puis ouvrir `login.html` dans un navigateur (ou avec Live Server).

## 👥 Comptes de Test

| Type | Username | Password |
|------|----------|----------|
| Gestionnaire | `jleclerc` | `securepass123` |
| Agent | `fhardy` | `agentpass456` |
| Pilote | `pdurand` | `pilote789` |

## 📊 Base de Données

### Tables principales
- **Pilote**, **Agent_d_exploitation**, **Gestionnaire** - Utilisateurs
- **Avion** - Aéronefs liés aux pilotes
- **Infrastructure** - Hangars, parkings (avec capacité)
- **Creneaux** - Table pivot : mouvement + infrastructure + facturation
- **Carburant** - AVGAS 100LL, JET A-1
- **Facture**, **Avitaillement**, **Messagerie**

## 🔍 Points Clés pour la Présentation

### 1. Séparation des responsabilités
- **`main.py`**: API REST (HTTP)
- **`business.py`**: Logique métier pure (pas de SQL)
- **`CRUD.py`**: Accès base de données

### 2. Validation métier
```python
# Exemple: Vérification des 90 minutes
is_valid, error = validate_creneau_time_slot(
    db, infrastructure_id, debut, fin
)
```

### 3. RBAC simplifié
```python
@app.post("/creneaux/", dependencies=[Depends(is_pilote)])
@app.put("/creneaux/{id}", dependencies=[Depends(is_agent)])
```

## 📝 Scripts Utilitaires

## 📝 Scripts Utilitaires

```bash
# Afficher toute la base de données
python display_full_db.py

# Vider toutes les tables
python empty_db.py

# Inspecter le schéma
python inspect_db.py

# Ajouter un utilisateur manuellement
python add_user.py
```

## 🎯 Choix de Simplification

Pour la présentation, le projet a été simplifié tout en conservant les fonctionnalités essentielles:

✅ **Conservé:**
- Règle des 90 minutes (cœur métier)
- Authentification bcrypt + JWT
- Séparation business.py / main.py
- RBAC à 3 niveaux
- Calcul automatique de facturation

✨ **Simplifié:**
- Modèles Pydantic (2 au lieu de 4 par entité)
- Validation simplifiée sur certains endpoints
- Documentation inline pour faciliter la compréhension


## 📖 Documentation API Interactive

La documentation Swagger est disponible à : `http://127.0.0.1:8000/docs`

---

**Projet réalisé pour IPSA - Présentation académique**
