# ✈️ Documentation du Projet : Système de Gestion d'Aérodrome

Ce document détaille l'architecture, les fonctionnalités et l'implémentation technique du système de gestion d'aérodrome, en se basant sur les objectifs initiaux et le code source du projet.

---

## 🛠️ Architecture Technique

Le projet est construit sur une architecture client-serveur moderne utilisant Python et FastAPI pour le backend, et une interface web simple en HTML/JavaScript pour le frontend.

*   **Langage Backend :** Python 3
*   **Framework API :** FastAPI
*   **Base de Données :** SQLite (`Code_SQlite.db`)
*   **Architecture :** API RESTful
*   **Frontend :** HTML, CSS, JavaScript (pour l'interaction avec l'API)
*   **Gestion des mots de passe :** Hachage avec `bcrypt` via la librairie `passlib`.

---

## 🗄️ Structure de la Base de Données

La base de données SQLite est définie dans le fichier `create_db.py`. Elle est conçue pour stocker toutes les informations relatives aux utilisateurs, aux infrastructures, aux opérations et à la facturation. Le script `populate_db.py` remplit la base avec un jeu de données de démonstration.

### Schéma des Tables

*   **`Carburant`**: Stocke les types de carburant et leur prix au litre.
*   **`Infrastructure`**: Décrit les infrastructures disponibles (hangars, parkings) avec leurs capacités et tarifs.
*   **`Gestionnaire`**, **`Pilote`**, **`Agent_d_exploitation`**: Tables pour les trois types d'utilisateurs, avec leurs informations personnelles et leurs mots de passe hachés.
*   **`Avion`**: Contient les informations sur les aéronefs, liés à un pilote et à un type de carburant.
*   **`Avitaillement`**: Enregistre les opérations d'avitaillement en carburant.
*   **`Facture`**: Contient les informations sur les factures émises.
*   **`Creneaux`**: Table centrale qui lie les mouvements des aéronefs, les pilotes, les infrastructures utilisées et les factures associées.
*   **`Messagerie`**: Permet un échange de messages entre les pilotes et les agents d'exploitation.

---

## 🚀 API RESTful (Backend)

Le backend est développé avec FastAPI et fournit une série de points d'accès (endpoints) pour interagir avec la base de données. Le code se trouve principalement dans `api/main.py` et `api/models.py`.

### Fonctionnalités Clés de l'API

*   **Authentification :** Un endpoint `/login` permet aux utilisateurs de se connecter en vérifiant leur nom d'utilisateur et leur mot de passe. Le type d'utilisateur est retourné en cas de succès.
*   **Opérations CRUD :** Des endpoints CRUD (Create, Read, Update, Delete) complets sont disponibles pour la plupart des tables de la base de données (Pilotes, Avions, Infrastructures, etc.).
*   **Modèles Pydantic :** Le fichier `api/models.py` définit des modèles Pydantic pour la validation des données entrantes et sortantes de l'API, garantissant ainsi la cohérence des données.
*   **Gestion des Erreurs :** L'API utilise les exceptions HTTP de FastAPI pour retourner des codes d'erreur appropriés (e.g., 404 Not Found, 401 Unauthorized).

---

## 🖥️ Interface Utilisateur (Frontend)

L'interface utilisateur est constituée de trois pages HTML principales qui interagissent avec l'API via des requêtes JavaScript (`fetch`).

*   **`login.html`**: Une page de connexion simple avec un style "terminal" où les utilisateurs peuvent entrer leurs identifiants. En cas de succès, l'utilisateur est redirigé vers le tableau de bord.
*   **`dashboard.html`**: Le tableau de bord affiche un message de bienvenue et des options en fonction du type d'utilisateur connecté (Gestionnaire, Agent, Pilote). Par exemple, un gestionnaire peut créer de nouveaux utilisateurs (gestionnaires, agents, pilotes), tandis qu'un agent ne peut créer que des pilotes.
*   **`create_user.html`**: Une page dynamique pour la création de nouveaux utilisateurs. Le formulaire s'adapte en fonction du type d'utilisateur à créer (par exemple, des champs supplémentaires pour la licence et l'aptitude médicale pour un pilote).

---

## ✨ Fonctionnalités Implémentées

Le projet couvre une grande partie des objectifs initiaux :

*   **Gestion des utilisateurs :** Création, authentification et gestion des différents types d'utilisateurs avec des droits distincts (implémentés côté frontend).
*   **CRUD complet :** La classe `DatabaseManager` dans `CRUD.py` fournit une interface robuste pour toutes les opérations de base de données.
*   **API fonctionnelle :** Une API RESTful complète et fonctionnelle avec FastAPI.
*   **Interface basique :** Une interface utilisateur fonctionnelle pour la connexion, la création d'utilisateurs et la navigation.
*   **Structure de données complète :** La base de données reflète fidèlement le modèle de données nécessaire pour la gestion de l'aérodrome.

---

## 🔮 Pistes d'Améliorations (basées sur `objectifs.md`)

Certaines fonctionnalités avancées listées dans `objectifs.md` ne sont pas encore implémentées dans le code fourni :

*   **Logique de gestion des créneaux :** La vérification de l'intervalle de 90 minutes et le cycle de vie des états de créneaux (`Demandé`, `Confirmé`, etc.) ne sont pas implémentés dans l'API.
*   **Calculs automatiques :** Le calcul automatique du `cout_total` pour les créneaux n'est pas présent.
*   **Reporting et statistiques :** Les fonctionnalités de visualisation des flux et des revenus pour les gestionnaires ne sont pas développées.
*   **Interface plus riche :** Le frontend pourrait être étendu pour inclure la gestion des avions, la demande de créneaux, la consultation des factures, etc.

---

## 📝 Note sur le MCD / MLD

Conformément à la demande, il est à noter que les diagrammes de **Modèle Conceptuel de Données (MCD)** et de **Modèle Logique de Données (MLD)** ont été réalisés séparément de ce projet de codage et ne sont donc pas inclus dans ce dépôt.
