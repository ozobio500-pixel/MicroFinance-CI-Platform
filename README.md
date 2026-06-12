# COFINANCE CI — Plateforme digitale de microfinance

API REST Django 5 + Django REST Framework, authentification JWT, chat en temps réel WebSocket (Django Channels + Daphne), base SQLite en développement, PostgreSQL configurable.

---

## Prérequis

- Python 3.11+
- pip
- Git

---

## Installation

```bash
git clone <url-du-depot>
cd "MicroFinance CI Platform"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
```

---

## Lancement

```bash
python manage.py runserver
```

daphne est placé en tête de INSTALLED_APPS : Django utilise ASGI automatiquement, le chat WebSocket fonctionne sans commande supplémentaire.

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/api/docs/ | Documentation Swagger (OAS 3.0) |
| http://127.0.0.1:8000/chat/ | Interface chat temps réel |
| http://127.0.0.1:8000/api/schema/ | Schéma OpenAPI brut |

---

## Comptes de démonstration

Créés automatiquement par `python manage.py seed_db`.

| Utilisateur | Rôle | Mot de passe |
|-------------|------|--------------|
| `admin` | Administrateur | `demo1234` |
| `agent1` | Agent de terrain | `demo1234` |
| `client1` | Client | `demo1234` |

Authentification : POST /api/auth/token/ avec username et password, retourne le token JWT (champ access).

---

## Modules fonctionnels

| N° | Module | Endpoints principaux |
|----|--------|----------------------|
| 01 | Authentification et Profils | /api/auth/token/, /api/accounts/me/ |
| 02 | Microcrédits | /api/microcredits/applications/ |
| 03 | Remboursements | /api/repayments/installments/ |
| 04 | Assurance mobile | /api/insurance/products/, /api/insurance/subscribe/ |
| 05 | Tableau de bord | /api/dashboard/kpis/ |
| 06 | Notifications | /api/notifications/ |
| 07 | Chat temps réel | /chat/ + WebSocket ws://localhost:8000/ws/chat/{id}/ |

---

## Démonstration du chat WebSocket

1. Lancer le serveur : python manage.py runserver
2. Ouvrir deux onglets sur http://127.0.0.1:8000/chat/
3. Onglet 1 : se connecter avec client1 / demo1234
4. Onglet 2 : se connecter avec admin / demo1234
5. Sélectionner la même conversation dans les deux onglets
6. Envoyer un message : il apparaît instantanément dans l'autre onglet

---

## Commandes de gestion

```bash
# Données de démonstration
python manage.py seed_db

# Alertes remboursement J-3 et J+1
python manage.py check_installment_alerts

# Alertes expiration assurance 15 jours avant terme
python manage.py check_insurance_expiry
```

---

## Configuration PostgreSQL

```bash
set DB_ENGINE=django.db.backends.postgresql
set DB_NAME=cofinance
set DB_USER=postgres
set DB_PASSWORD=secret
set DB_HOST=localhost
set DB_PORT=5432
```

Puis installer le driver : pip install psycopg2-binary

---

## Stack technique

- Backend : Python 3.11, Django 5.x, Django REST Framework
- Auth : JWT via djangorestframework-simplejwt
- WebSocket : Django Channels + Daphne
- Documentation API : drf-spectacular (Swagger / ReDoc)
- Base de données : SQLite (dev) vers PostgreSQL (prod)
- Versioning : Git / GitHub
