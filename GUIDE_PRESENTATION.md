# Guide de Présentation - Projet Gestion Aérodrome IPSA

## 🎯 Objectif de la Présentation
Présenter un système complet de gestion d'aérodrome avec base de données, en mettant l'accent sur l'architecture, les fonctionnalités métier et la démonstration pratique.

---

## 📋 Structure de la Présentation (15-20 minutes)

### 1. Introduction (2 minutes)
**Qui présente quoi :** Personne 1

**Contenu oral :**
- Contexte du projet : problématique de gestion d'un aérodrome
- Objectifs principaux du système
- Technologies utilisées (vue d'ensemble rapide)

**PowerPoint - Slide 1-2 :**
- **Slide 1 :** Titre du projet + noms + logo IPSA
- **Slide 2 :** 
  - Problématique (bullet points)
  - Stack technique (logos : Python, FastAPI, PostgreSQL, HTML/CSS/JS)
  - Architecture globale (schéma simple : Frontend ↔ API ↔ Base de données)

---

### 2. Architecture du Système (3-4 minutes)
**Qui présente quoi :** Personne 2

**Contenu oral :**
- Explication de l'architecture 3-tiers
- Rôle de chaque couche
- Choix techniques et justifications

**PowerPoint - Slide 3-4 :**
- **Slide 3 - Architecture 3-tiers :**
  ```
  ┌─────────────────┐
  │   Frontend      │ (Interface utilisateur)
  │  HTML/CSS/JS    │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │   API REST      │ (Logique métier)
  │   FastAPI       │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │  Base de        │ (Persistance)
  │  Données        │
  └─────────────────┘
  ```

- **Slide 4 - Technologies clés :**
  - **API REST** : FastAPI pour les endpoints performants
  - **Base de données** : PostgreSQL avec contraintes d'intégrité
  - **ORM** : SQLAlchemy pour l'abstraction BDD
  - **Validation** : Pydantic pour la sécurité des données

---

### 3. Modélisation de la Base de Données (4-5 minutes)
**Qui présente quoi :** Personne 1

**Contenu oral :**
- Présentation du schéma de base de données
- Explication des entités principales
- Relations et contraintes importantes
- Justification des choix de modélisation

**PowerPoint - Slide 5-6 :**
- **Slide 5 - Diagramme Entité-Association :**
  - Schéma visuel des tables principales
  - Relations (1-N, N-N)
  
- **Slide 6 - Entités principales :**
  | Entité | Rôle | Attributs clés |
  |--------|------|----------------|
  | Pilote | Utilisateur réservant des créneaux | email, licence |
  | Avion | Ressource à réserver | immatriculation, consommation |
  | Creneau | Réservation de vol | date, durée, état |
  | Infrastructure | Équipements aérodrome | type, disponibilité |
  | Avitaillement | Gestion carburant | quantité, coût |

---

### 4. Règles Métier et Logique Applicative (3-4 minutes)
**Qui présente quoi :** Personne 2

**Contenu oral :**
- Règles métier implémentées
- Logique de validation
- Workflows automatisés

**PowerPoint - Slide 7-8 :**
- **Slide 7 - Règles Métier :**
  - ✅ **Règle des 90 minutes** : créneaux maximum de 1h30
  - ✅ **Calcul automatique des coûts** : durée × consommation × prix carburant
  - ✅ **Gestion des états** : brouillon → confirmé → terminé → achevé
  - ✅ **Contraintes de disponibilité** : vérification avion/infrastructure

- **Slide 8 - Workflow de Réservation :**
  ```
  Pilote crée creneau (brouillon)
         ↓
  Validation automatique (durée, dispo)
         ↓
  Agent confirme le creneau
         ↓
  Calcul coût automatique
  ```

---

### 5. Gestion des Utilisateurs et Permissions (2-3 minutes)
**Qui présente quoi :** Personne 1

**Contenu oral :**
- Différents rôles dans le système
- Permissions spécifiques
- Sécurité et authentification

**PowerPoint - Slide 9 :**
- **Slide 9 - Rôles et Permissions :**
  
  | Rôle | Permissions |
  |------|-------------|
  | **Pilote** | Créer/consulter ses créneaux, voir coûts |
  | **Agent d'Exploitation** | Modifier états créneaux, gérer avitaillement |
  | **Gestionnaire** | Consulter statistiques, gérer infrastructures, vue d'ensemble |

---

### 6. Démonstration Pratique (5-6 minutes)
**Qui présente quoi :** Les deux (écran partagé)

**Contenu oral :**
- Démonstration live de l'application
- Parcours utilisateur complet

**PowerPoint - Slide 10 (optionnel - captures d'écran) :**
- **Slide 10 - Interfaces Utilisateur :**
  - Screenshots du dashboard pilote
  - Screenshots du panel agent
  - Screenshots du panel gestionnaire

**Scénario de démo :**
1. **Connexion Pilote** → Dashboard
2. **Créer une réservation** → Sélection avion, date, durée
3. **Validation automatique** → Vérification règle 90 min
4. **Connexion Agent** → Voir créneaux en attente
5. **Confirmer creneau** → Changement d'état
6. **Voir le coût calculé** automatiquement
7. **Connexion Gestionnaire** → Vue d'ensemble statistiques

---

### 7. Points Techniques Intéressants (2-3 minutes)
**Qui présente quoi :** Personne 2

**Contenu oral :**
- Défis techniques rencontrés
- Solutions implémentées
- Optimisations

**PowerPoint - Slide 11 :**
- **Slide 11 - Défis & Solutions :**
  - 🔧 **Calcul de coûts complexe** → Fonction business.py centralisée
  - 🔧 **Gestion des états** → Machine à états avec validations
  - 🔧 **Performance requêtes** → Indexation sur dates et FK
  - 🔧 **Validation données** → Pydantic models côté API

---

### 8. Conclusion et Perspectives (1-2 minutes)
**Qui présente quoi :** Personne 1

**Contenu oral :**
- Récapitulatif des objectifs atteints
- Limitations actuelles
- Améliorations futures possibles

**PowerPoint - Slide 12-13 :**
- **Slide 12 - Objectifs Atteints :**
  - ✅ Base de données normalisée et fonctionnelle
  - ✅ API REST complète avec CRUD
  - ✅ Interface utilisateur multi-rôles
  - ✅ Règles métier automatisées
  - ✅ Système de calcul des coûts

- **Slide 13 - Perspectives :**
  - 📈 Statistiques et tableaux de bord avancés
  - 📧 Système de notifications email
  - 📱 Application mobile
  - 🔐 Authentification OAuth2/JWT

---

## 🎨 Conseils PowerPoint

### Design
- **Thème** : Professionnel, épuré (couleurs bleu/blanc ou aviation)
- **Police** : Calibri ou Arial, taille 24+ pour le texte
- **Illustrations** : Icônes d'avions, tours de contrôle pour l'ambiance

### Contenu par slide
- **Maximum 5-6 bullet points** par slide
- **Schémas plutôt que texte** quand possible
- **Captures d'écran** de l'application réelle
- **Code minimal** : éviter le code, privilégier les schémas

### Animations
- **Transitions simples** (fade)
- **Apparition progressive** des bullet points pour guider l'attention

---

## 📌 Répartition du Travail Suggérée

### Personne 1
- Introduction
- Modélisation BDD
- Gestion utilisateurs
- Conclusion
- **Préparation :** Slides 1-2, 5-6, 9, 12-13

### Personne 2
- Architecture
- Règles métier
- Points techniques
- **Préparation :** Slides 3-4, 7-8, 11

### Ensemble
- Démonstration pratique
- **Préparation :** Slide 10 + Application fonctionnelle

---

## ✅ Checklist Avant Présentation

### Technique
- [ ] Application fonctionne localement
- [ ] Base de données peuplée avec données de démo
- [ ] Toutes les fonctionnalités marchent (test complet)
- [ ] Connexions rapides (comptes pré-créés)

### PowerPoint
- [ ] Toutes les slides créées
- [ ] Orthographe vérifiée
- [ ] Schémas clairs et lisibles
- [ ] Transitions testées

### Oral
- [ ] Timing répété (15-20 min max)
- [ ] Transitions entre orateurs fluides
- [ ] Questions potentielles anticipées
- [ ] Backup plan si démo plante

---

## 💡 Questions Potentielles à Anticiper

1. **"Pourquoi PostgreSQL plutôt qu'une autre BDD ?"**
   - Robustesse, contraintes d'intégrité, support complexe (Note: Bien que SQLite soit utilisé pour la démo, PostgreSQL est souvent cité comme l'étape suivante logique).

2. **"Comment gérez-vous la sécurité ?"**
   - Validation Pydantic, contraintes BDD, séparation des rôles (RBAC), hachage bcrypt.

3. **"Scalabilité du système ?"**
   - Architecture modulaire, API REST permet la distribution des services.

4. **"Pourquoi FastAPI ?"**
   - Performance, documentation automatique (Swagger), validation native.

5. **"Gestion des conflits de réservation ?"**
   - Vérification systématique de la disponibilité et de la règle des 90 minutes avant toute confirmation.

---

## 🎯 Objectif Final

> Montrer que vous maîtrisez :
> - La conception de base de données relationnelle
> - L'architecture d'une application complète
> - L'implémentation de règles métier complexes
> - Le développement full-stack

**Bonne présentation ! 🚀**
