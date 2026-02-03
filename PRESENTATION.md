# 🎯 Guide de Présentation - Système de Gestion d'Aérodrome

## 🎬 Démonstration en 5 Minutes

### 1. Introduction (30 secondes)
> "Application web de gestion d'aérodrome avec 3 fonctionnalités clés : authentification multi-rôles, validation automatique des créneaux avec intervalle de sécurité de 90 minutes, et calcul automatique de facturation."

**Stack technique:**
- Backend: FastAPI (Python)
- BDD: SQLite
- Frontend: HTML/JS vanilla
- Sécurité: JWT + bcrypt

---

### 2. Architecture (1 minute)

#### Séparation des responsabilités
```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│   main.py   │────▶│ business.py  │────▶│ CRUD.py  │
│   (API)     │     │  (Logique)   │     │  (BDD)   │
└─────────────┘     └──────────────┘     └──────────┘
```

**Montrer dans le code:**
1. Ouvrir `api/main.py` ligne 1 - header de documentation
2. Ouvrir `business.py` ligne 1 - commentaires des 4 fonctions clés

---

### 3. ⭐ Fonction 1: Authentification Multi-Rôles (1 minute)

**Démonstration live:**
1. Ouvrir `login.html`
2. Se connecter avec `jleclerc` / `securepass123` (Gestionnaire)
3. Montrer les 3 boutons de création utilisateur

**Expliquer le code:**
```python
# business.py - ligne 35
def authenticate_user(db, username, password):
    """Vérifie dans 3 tables: Pilote, Agent, Gestionnaire"""
    # Vérification avec bcrypt
    if verify_password(password, hash):
        return {"id": ..., "type": "gestionnaire"}
```

**Points clés:**
- 3 niveaux de privilèges (0, 1, 2)
- Bcrypt pour le hashing
- JWT tokens (30 min)

---

### 4. ⭐ Fonction 2: Règle des 90 Minutes (1.5 minutes)

**C'est LA règle métier centrale !**

**Démonstration:**
1. Se connecter en tant que pilote
2. Tenter de créer un créneau
3. Montrer l'erreur si conflit

**Code à montrer:**
```python
# business.py - ligne 111
def validate_creneau_time_slot(db, infrastructure_id, debut, fin):
    """⭐ RÈGLE DES 90 MINUTES ⭐"""
    for existing_creneau in all_creneaux:
        # Vérifier qu'il y a 90 min entre les créneaux
        if (debut < existing_fin + timedelta(minutes=90)) and 
           (fin > existing_debut - timedelta(minutes=90)):
            return False, "Conflict!"
```

**Expliquer:**
- Sécurité aérienne = intervalle minimum entre mouvements
- Validation AVANT création en base
- Appliquée automatiquement par l'API

---

### 5. ⭐ Fonction 3: Calcul Automatique de Coût (1 minute)

**Code à montrer:**
```python
# business.py - ligne 65
def calculate_creneau_cost(db, infrastructure_id, ...):
    """Calcul: infrastructure + avitaillement"""
    # Tarification dégressive
    if days >= 30:
        total_cost += (days/30) * prix_mois
    elif days >= 7:
        total_cost += (days/7) * prix_semaine
    else:
        total_cost += days * prix_jour
```

**Points clés:**
- Automatique lors de la création/mise à jour
- Tarification dégressive (jour < semaine < mois)
- Stocké dans `cout_total`

---

### 6. Sécurité & RBAC (30 secondes)

**Montrer dans `main.py`:**
```python
# Ligne 153+
@app.post("/creneaux/", dependencies=[Depends(is_pilote)])
@app.put("/creneaux/{id}", dependencies=[Depends(is_agent)])
```

**Expliquer:**
- Gestionnaire: tout faire ✅
- Agent: valider créneaux, facturer ✅
- Pilote: créer créneaux, gérer ses avions ✅

---

## 📊 Schéma Base de Données (si demandé)

```
Pilote ────┐
           ├──▶ Avion ────▶ Creneaux ◀──── Infrastructure
Agent ─────┤                   │
           │                   ▼
Gestionnaire                Facture
```

**Tables clés:**
- `Creneaux` = table pivot centrale
- `Carburant` = AVGAS 100LL, JET A-1
- `Messagerie` = Pilote ↔ Agent

---

## 🎓 Justification des Choix

### Pourquoi FastAPI ?
- Documentation auto-générée (Swagger)
- Validation automatique avec Pydantic
- Async natif (performances)

### Pourquoi SQLite ?
- Simplicité pour prototype
- Pas de serveur à gérer
- Facile à démontrer

### Pourquoi séparer business.py ?
- **Maintenabilité**: logique métier isolée
- **Testabilité**: pas de dépendances HTTP
- **Clarté**: facile à expliquer lors de la présentation

---

## 💡 Questions Fréquentes

**Q: Pourquoi 90 minutes précisément ?**
R: Marge de sécurité aéronautique standard pour préparer infrastructure entre mouvements.

**Q: Pourquoi JWT et pas sessions ?**
R: Stateless = scalable, pas de stockage serveur, expiration automatique.

**Q: Pourquoi 3 niveaux de privilèges ?**
R: Reflète organisation réelle aérodrome: direction, exploitation, utilisateurs.

**Q: Performance avec SQLite ?**
R: Suffisant pour petit aérodrome (<100 mouvements/jour). Production = PostgreSQL.

---

## 🚀 Pour Aller Plus Loin

**Améliorations possibles:**
- WebSockets pour notifications temps réel
- Reporting/analytics pour gestionnaire
- Export PDF des factures
- API REST pour météo
- Interface mobile

**Production:**
- PostgreSQL au lieu de SQLite
- Docker + Kubernetes
- HTTPS obligatoire
- Rate limiting
- Logs centralisés

---

## 📝 Checklist Présentation

- [ ] Serveur lancé (`uvicorn api.main:app --reload`)
- [ ] Base de données peuplée (`python populate_db.py`)
- [ ] Navigateur ouvert sur `login.html`
- [ ] Code éditeur prêt sur `business.py`
- [ ] Diagramme MCD/MLD imprimé (si requis)
- [ ] Terminal visible pour logs en temps réel

---

**🎯 Message final:**
> "Projet démontrant une architecture claire, une logique métier robuste avec la règle des 90 minutes, et un système d'authentification sécurisé - le tout dans un code simple à comprendre et à présenter."
