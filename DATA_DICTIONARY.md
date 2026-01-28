# Dictionnaire de Données du Projet de Gestion d'Aéroport

Ce document détaille la structure de la base de données `Code_SQlite.db`, générée par `create_db.py`. Il fournit une description pour chaque table et ses colonnes, y compris les types de données, les contraintes et les relations.

---

## Tables de Référence

### `Carburant`

| Colonne | Type | Contraintes | Description |
| :------ | :--- | :---------- | :---------- |
| `Nom` | TEXT | PK, NOT NULL | Nom unique du type de carburant (ex: AVGAS 100LL, JET A-1). |
| `prix_par_l` | REAL | NOT NULL | Prix par litre de ce type de carburant. |

### `Infrastructure`

| Colonne | Type | Contraintes | Description |
| :-------- | :----- | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique de l'infrastructure. |
| `nom` | TEXT | NOT NULL | Nom de l'infrastructure (ex: Hangar H1-A, Parking P1-Nord). |
| `type` | TEXT | NOT NULL | Type de l'infrastructure (ex: Hangar, Parking, Piste). |
| `capacite_max` | INTEGER | NOT NULL | Capacité maximale de l'infrastructure (nombre d'aéronefs). |
| `prix_jour` | REAL | NOT NULL | Tarif journalier de l'infrastructure. |
| `prix_semaine` | REAL | NOT NULL | Tarif hebdomadaire de l'infrastructure. |
| `prix_mois` | REAL | NOT NULL | Tarif mensuel de l'infrastructure. |

---

## Tables d'Utilisateurs

### `Gestionnaire`

| Colonne | Type | Contraintes | Description |
| :------------ | :------ | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique du gestionnaire. |
| `nom` | TEXT | NOT NULL | Nom de famille du gestionnaire. |
| `prenom` | TEXT | NOT NULL | Prénom du gestionnaire. |
| `tel` | TEXT | NOT NULL | Numéro de téléphone du gestionnaire. |
| `mail` | TEXT | NOT NULL | Adresse e-mail du gestionnaire. |
| `username` | TEXT | NOT NULL, UNIQUE | Nom d'utilisateur unique pour la connexion. |
| `password_hash` | TEXT | NOT NULL | Hash du mot de passe pour la sécurité. |

### `Pilote`

| Colonne | Type | Contraintes | Description |
| :------------ | :------ | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique du pilote. |
| `nom` | TEXT | NOT NULL | Nom de famille du pilote. |
| `prenom` | TEXT | NOT NULL | Prénom du pilote. |
| `tel` | TEXT | NOT NULL | Numéro de téléphone du pilote. |
| `mail` | TEXT | NOT NULL | Adresse e-mail du pilote. |
| `username` | TEXT | NOT NULL, UNIQUE | Nom d'utilisateur unique pour la connexion. |
| `license` | TEXT | NOT NULL | Numéro ou type de licence de pilotage. |
| `medical` | TEXT | NOT NULL | Informations sur l'aptitude médicale du pilote. |
| `password_hash` | TEXT | NOT NULL | Hash du mot de passe pour la sécurité. |

### `Agent_d_exploitation`

| Colonne | Type | Contraintes | Description |
| :------------ | :------ | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique de l'agent d'exploitation. |
| `nom` | TEXT | NOT NULL | Nom de famille de l'agent. |
| `prenom` | TEXT | NOT NULL | Prénom de l'agent. |
| `tel` | TEXT | NOT NULL | Numéro de téléphone de l'agent. |
| `mail` | TEXT | NOT NULL | Adresse e-mail de l'agent. |
| `username` | TEXT | NOT NULL, UNIQUE | Nom d'utilisateur unique pour la connexion. |
| `password_hash` | TEXT | NOT NULL | Hash du mot de passe pour la sécurité. |

---

## Tables Opérationnelles

### `Avion`

| Colonne | Type | Contraintes | Description |
| :---------------- | :------ | :---------- | :---------- |
| `Immatriculation` | TEXT | PK, NOT NULL | Immatriculation unique de l'aéronef. |
| `marque` | TEXT | NOT NULL | Marque de l'avion. |
| `modele` | TEXT | NOT NULL | Modèle de l'avion. |
| `dimension` | TEXT | NOT NULL | Dimensions de l'avion. |
| `poids` | TEXT | NOT NULL | Poids de l'avion. |
| `carburant_id` | TEXT | FK (`Carburant.Nom`), ON DELETE SET NULL | Type de carburant utilisé par l'avion. |
| `pilote_id` | INTEGER | FK (`Pilote.Id`), ON DELETE CASCADE | Pilote propriétaire de l'avion. Si le pilote est supprimé, l'avion l'est aussi. |

### `Avitaillement`

| Colonne | Type | Contraintes | Description |
| :-------------- | :----- | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique de l'opération d'avitaillement. |
| `date` | TEXT | NOT NULL | Date de l'avitaillement (format YYYY-MM-DD). |
| `heure` | TEXT | NOT NULL | Heure de l'avitaillement (format HH:MM). |
| `quantite_en_l` | REAL | NOT NULL | Quantité de carburant en litres. |
| `cout` | REAL | NOT NULL | Coût total de l'avitaillement. |
| `avion_id` | TEXT | FK (`Avion.Immatriculation`), ON DELETE CASCADE | L'avion qui a été avitaillé. Si l'avion est supprimé, l'avitaillement l'est aussi. |

### `Facture`

| Colonne | Type | Contraintes | Description |
| :---------------- | :------ | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique de la facture. |
| `rib` | TEXT | NOT NULL | Numéro RIB pour le paiement. |
| `date_d_emission` | TEXT | NOT NULL | Date d'émission de la facture (format YYYY-MM-DD). |
| `agent_id` | INTEGER | FK (`Agent_d_exploitation.Id`), ON DELETE SET NULL | Agent qui a émis la facture. Si l'agent est supprimé, le lien est mis à NULL. |

### `Messagerie`

| Colonne | Type | Contraintes | Description |
| :-------------- | :----- | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique du message. |
| `date` | TEXT | NOT NULL | Date d'envoi du message (format YYYY-MM-DD). |
| `heure` | TEXT | NOT NULL | Heure d'envoi du message (format HH:MM). |
| `contenu` | TEXT | NOT NULL | Contenu textuel du message. |
| `sens_d_envoie` | INTEGER | NOT NULL | Indique l'expéditeur (ex: 0 pour Agent, 1 pour Pilote). |
| `agent_id` | INTEGER | FK (`Agent_d_exploitation.Id`), ON DELETE SET NULL | Agent impliqué dans la conversation. Si l'agent est supprimé, le lien est mis à NULL. |
| `pilote_id` | INTEGER | FK (`Pilote.Id`), ON DELETE SET NULL | Pilote impliqué dans la conversation. Si le pilote est supprimé, le lien est mis à NULL. |

### `Creneaux` (Table Centrale / Pivot)

| Colonne | Type | Contraintes | Description |
| :---------------- | :----- | :---------- | :---------- |
| `Id` | INTEGER | PK, AUTOINCREMENT | Identifiant unique du créneau. |
| `debut_prevu` | TEXT | NOT NULL | Date et heure de début prévue (ISO format). |
| `fin_prevu` | TEXT | NOT NULL | Date et heure de fin prévue (ISO format). |
| `debut_reel` | TEXT | | Date et heure de début réelle (ISO format, optionnel). |
| `fin_reel` | TEXT | | Date et heure de fin réelle (ISO format, optionnel). |
| `etat` | TEXT | NOT NULL | État actuel du créneau (Demandé, Confirmé, Autorisé, Achevé, Annulé). |
| `cout_total` | REAL | | Coût total calculé du créneau (infrastructure + avitaillement). |
| `avitaillement_id` | INTEGER | FK (`Avitaillement.Id`), ON DELETE SET NULL | Lien vers une opération d'avitaillement. Si l'avitaillement est supprimé, le lien est mis à NULL. |
| `pilote_id` | INTEGER | FK (`Pilote.Id`), ON DELETE CASCADE | Pilote ayant réservé le créneau. Si le pilote est supprimé, le créneau l'est aussi. |
| `infrastructure_id` | INTEGER | FK (`Infrastructure.Id`), ON DELETE SET NULL | Infrastructure réservée. Si l'infrastructure est supprimée, le lien est mis à NULL. |
| `facture_id` | INTEGER | FK (`Facture.Id`), ON DELETE SET NULL | Facture associée à ce créneau. Si la facture est supprimée, le lien est mis à NULL. |