# Epic Events CRM

Application en ligne de commande (CLI) permettant à Epic Events de gérer de manière sécurisée ses clients, contrats et événements. Projet réalisé dans le cadre de la formation Python RNCP d'OpenClassrooms (Projet 12 — Développez une architecture back-end sécurisée avec Python et SQL).

## Stack technique

- **Python 3** + **SQLAlchemy 2.0** (ORM) + **psycopg** (driver PostgreSQL)
- **PostgreSQL**
- **Argon2** (`argon2-cffi`) pour le hachage des mots de passe
- **PyJWT** pour l'authentification persistante (jetons JWT)
- **Typer** + **Rich** pour l'interface en ligne de commande
- **Sentry** pour la journalisation des exceptions et des événements métier sensibles
- **pytest** + **pytest-cov** pour les tests automatisés

## Prérequis

- Python 3.11 ou supérieur
- PostgreSQL installé et accessible en local (ou distant)
- *(optionnel)* Un compte Sentry (gratuit) avec un projet Python dédié, pour la journalisation — l'application fonctionne normalement sans, la journalisation Sentry est simplement désactivée

## Installation

### 1. Cloner le dépôt et créer l'environnement virtuel

```bash
git clone <url-du-repo>
cd pyOCP12
python -m venv .venv
```

Activation du venv :
- Windows (PowerShell) : `.venv\Scripts\Activate.ps1`
- macOS/Linux : `source .venv/bin/activate`

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer la base de données PostgreSQL

Créer une base dédiée et un compte applicatif **non privilégié** (pas de superuser), avec les droits nécessaires sur cette base et son schéma :

```sql
CREATE DATABASE epicevents;
CREATE ROLE epicevents_app WITH LOGIN PASSWORD 'un_mot_de_passe_solide';
GRANT ALL PRIVILEGES ON DATABASE epicevents TO epicevents_app;
\c epicevents
GRANT ALL PRIVILEGES ON SCHEMA public TO epicevents_app;
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet (jamais commité) :

```
DATABASE_URL=postgresql+psycopg://epicevents_app:un_mot_de_passe_solide@localhost/epicevents
JWT_SECRET=une_valeur_aleatoire_longue_et_secrete
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

`DATABASE_URL` et `JWT_SECRET` sont obligatoires. `JWT_SECRET` peut être généré avec :
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`SENTRY_DSN` est **optionnel** : fourni par Sentry à la création d'un projet (plateforme **Python**) si vous voulez activer la journalisation. En son absence, l'application fonctionne normalement, elle n'envoie simplement rien à Sentry.

### 5. Créer les tables

```bash
python -c "from epicevents.database import init_db; init_db()"
```

### 6. Créer le premier compte (département gestion)

Aucun compte n'existant encore en base, il faut créer le tout premier collaborateur (département gestion) via le script de bootstrap dédié — la commande CLI normale de création de collaborateur exige déjà d'être connecté en tant que gestion, ce script contourne volontairement ce point de départ :

```bash
python -m scripts.seed_admin --numero-employe EMP001 --nom "Nom Prénom" --email admin@exemple.com --mot-de-passe "mot_de_passe_solide"
```

## Utilisation

```bash
python epicevents.py --help
```

Liste toutes les commandes disponibles. Se connecter d'abord :

```bash
python epicevents.py login <email>
```

Le mot de passe est demandé en saisie masquée. Un jeton d'authentification est ensuite stocké localement (`~/.epicevents_token`) et réutilisé automatiquement par les commandes suivantes, jusqu'à expiration (24h) ou déconnexion (`python epicevents.py logout`).

### Aperçu des commandes

| Domaine | Commandes |
|---|---|
| Authentification | `login`, `logout` |
| Clients | `list-clients`, `create-client`, `update-client` |
| Contrats | `list-contracts`, `list-unsigned-contracts`, `list-unpaid-contracts`, `create-contract`, `update-contract` |
| Événements | `list-events`, `list-events-without-support`, `list-my-events`, `create-event`, `assign-support`, `update-event` |
| Collaborateurs | `create-collaborateur`, `update-collaborateur` |

Les droits disponibles dépendent du département (rôle) du collaborateur connecté (commercial / support / gestion). Le détail de chaque commande est accessible via `python epicevents.py <commande> --help`.

## Tests

```bash
pytest
```

Avec couverture de code :

```bash
pytest --cov=epicevents --cov-report=term-missing
```

Les tests utilisent une base SQLite en mémoire, entièrement isolée de la base PostgreSQL réelle — aucun risque pour les données de production en les exécutant.

## Qualité de code

```bash
flake8 epicevents.py epicevents/ scripts/ tests/
black --check epicevents.py epicevents/ scripts/ tests/
```

## Sécurité

- Mots de passe collaborateurs hachés (Argon2), jamais stockés en clair.
- Authentification par jeton JWT signé, à durée de vie limitée (24h).
- Secrets (base de données, JWT, Sentry) exclusivement lus depuis les variables d'environnement, jamais en dur dans le code.
- Compte applicatif PostgreSQL non privilégié, distinct du compte superuser.
- Permissions vérifiées par rôle et, le cas échéant, par propriété (ex. un commercial ne peut modifier que ses propres clients) à chaque opération d'écriture.
- Requêtes systématiquement paramétrées via l'ORM SQLAlchemy — aucune concaténation de SQL.

## Schéma de la base de données

Voir `diag-classes.png` à la racine du projet.
