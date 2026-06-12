# 🧪 GUIDE DE TEST ET VALIDATION - COFINANCE CI

## ✅ Vérification Pre-Déploiement

Avant de démarrer le serveur, exécutez les commandes de vérification :

```bash
# 1. Vérifier la santé du système
python manage.py check

# Résultat attendu:
# System check identified no issues (0 silenced).
```

```bash
# 2. Vérifier les migrations
python manage.py migrate --plan

# Résultat attendu:
# Affiche le plan des migrations (migrations déjà appliquées)
```

```bash
# 3. Vérifier les données démo
python manage.py shell -c "from accounts.models import User; print(f'Users: {User.objects.count()}')"

# Résultat attendu:
# Users: 3 (admin, agent1, client1)
```

---

## 🚀 DÉMARRAGE DU SERVEUR

```bash
python manage.py runserver 8001
```

**Output attendu:**
```
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
[timestamp] Django version 5.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8001/
Quit the server with CTRL-BREAK.
```

---

## 🧪 SCÉNARIOS DE TEST

### TEST 1 — Chat Support (Principal)

#### Setup
1. Ouvrez deux onglets navigateur
2. **Onglet 1** (Client):
   - URL: http://localhost:8001/chat/
   - Username: `client1`
   - Password: `demo1234`
   - Cliquer "Se connecter"

3. **Onglet 2** (Agent):
   - URL: http://localhost:8001/chat/
   - Username: `admin`
   - Password: `demo1234`
   - Cliquer "Se connecter"

#### Étapes de Test

| # | Action | Résultat Attendu | Status |
|---|--------|-----------------|--------|
| 1 | Onglet 1: Voir conversation #1 dans la sidebar | Conversation "Support remboursement" visible | ✅ |
| 2 | Onglet 1: Cliquer sur la conversation | Historique des messages chargé (Bonjour, Bonjour comment puis-je vous aider) | ✅ |
| 3 | Onglet 1: Taper "Besoin d'aide" et Envoyer | Message apparaît immédiatement en vert (mine) | ✅ |
| 4 | Onglet 2: Actualiser (F5) et voir conversation | Message reçu en gris (theirs) en temps réel | ✅ |
| 5 | Onglet 2: Répondre "Bonjour, je vous écoute" | Message apparaît en vert côté agent | ✅ |
| 6 | Onglet 1: Voir réponse agent | Message en gris, badge "Agent en ligne" visible | ✅ |
| 7 | Onglet 2: Commencer à taper (sans envoyer) | Onglet 1: "L'agent tape un message..." apparaît | ✅ |
| 8 | Onglet 2: Attendre >1.5s sans envoyer | Onglet 1: Indicateur disparaît | ✅ |
| 9 | Fermer Onglet 2 | Onglet 1: Badge "Agent en ligne" disparaît | ✅ |

**Verdict**: Si tous les ✅, le chat fonctionne parfaitement en temps réel!

---

### TEST 2 — API REST

#### 2.1 Authentification
```bash
curl -X POST http://localhost:8001/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"client1","password":"demo1234"}'
```

**Résultat attendu:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2.2 Lister les Conversations
```bash
curl -X GET http://localhost:8001/api/support/conversations/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Résultat attendu:**
```json
[
  {
    "id": 1,
    "subject": "Support remboursement",
    "client_username": "client1",
    "assigned_agent_username": "admin",
    "status": "assigned",
    "messages": [
      {
        "id": 1,
        "sender": "client1",
        "content": "Bonjour.",
        "created_at": "2026-06-09T..."
      },
      ...
    ]
  }
]
```

#### 2.3 Lister les Demandes de Crédit
```bash
curl -X GET http://localhost:8001/api/microcredits/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Résultat attendu:**
```json
[
  {
    "id": 1,
    "client": 3,
    "amount": 350000,
    "duration_months": 6,
    "status": "disbursed",
    "eligibility_score": 68,
    "assigned_agent": 2,
    "created_at": "2026-06-09T..."
  }
]
```

#### 2.4 Documentation Swagger
**URL**: http://localhost:8001/api/docs/

**Vérifier:**
- ✅ Header avec logo Swagger
- ✅ Tous les endpoints listés
- ✅ Bouton "Try it out" fonctionnel
- ✅ Schémas des modèles visibles

---

### TEST 3 — Admin Django

#### URL: http://localhost:8001/admin/
**Identifiants**: `admin` / `demo1234`

#### Navigation & Vérifications

| Section | Vérification | Status |
|---------|--------------|--------|
| Users | ✅ 3 users (admin, agent1, client1) | ✅ |
| | ✅ Champs additionnels visibles (role, phone, region, credit_score) | ✅ |
| Credit Applications | ✅ 2 applications (1 disbursed, 1 submitted) | ✅ |
| | ✅ Filtre par status fonctionnel | ✅ |
| Repayment Installments | ✅ Versements affichés | ✅ |
| | ✅ Statut visible (pending, paid, late) | ✅ |
| Insurance Products | ✅ 2 produits (Vie Essentielle, Protection Famille) | ✅ |
| Insurance Subscriptions | ✅ Souscription active pour client1 | ✅ |
| Conversations | ✅ Conversation #1 créée | ✅ |
| | ✅ Messages persistants (2 messages) | ✅ |
| Notifications | ✅ Section visible (créée par seed_db) | ✅ |

---

### TEST 4 — Données de Démonstration

#### Vérifier la Seed

```bash
python manage.py shell << EOF
from accounts.models import User
from microcredits.models import CreditApplication
from repayments.models import RepaymentInstallment
from insurance.models import InsuranceProduct, InsuranceSubscription
from support.models import Conversation, Message

print(f"✅ Users: {User.objects.count()} (admin, agent1, client1)")
print(f"✅ Credit Apps: {CreditApplication.objects.count()} (2)")
print(f"✅ Installments: {RepaymentInstallment.objects.count()}")
print(f"✅ Insurance Products: {InsuranceProduct.objects.count()} (2)")
print(f"✅ Subscriptions: {InsuranceSubscription.objects.count()} (1)")
print(f"✅ Conversations: {Conversation.objects.count()} (1)")
print(f"✅ Messages: {Message.objects.count()} (2)")
EOF
```

**Résultat attendu:**
```
✅ Users: 3 (admin, agent1, client1)
✅ Credit Apps: 2 (2)
✅ Installments: 1
✅ Insurance Products: 2 (2)
✅ Subscriptions: 1 (1)
✅ Conversations: 1 (1)
✅ Messages: 2 (2)
```

---

### TEST 5 — Commandes de Gestion

#### 5.1 Vérifier les Alertes de Remboursement
```bash
python manage.py check_installment_alerts
```

**Résultat attendu:**
```
Checking installment alerts...
[Alertes pour versements à J-3, J+1, etc.]
```

#### 5.2 Vérifier les Expirations d'Assurance
```bash
python manage.py check_insurance_expiry
```

**Résultat attendu:**
```
Checking insurance expiry...
[Alertes pour assurances expirées/proches expiration]
```

---

## 🎯 CHECKLIST DE VALIDATION FINALE

### Avant Livraison
- [ ] `python manage.py check` → No issues
- [ ] Chat WebSocket fonctionne (2 onglets)
- [ ] API Swagger accessible
- [ ] Admin Django opérationnel
- [ ] Seed data complète
- [ ] README clair et complet
- [ ] requirements.txt à jour
- [ ] Git commits représentatifs

### Fonctionnalités Clés
- [ ] Authentification JWT
- [ ] Chat temps réel (WebSocket)
- [ ] Présence agent
- [ ] Indicateur de frappe
- [ ] Historique persistant
- [ ] API REST complète
- [ ] Admin Django complet
- [ ] Permissions par rôle

### Documentation
- [ ] API documentée (Swagger)
- [ ] README.md fourni
- [ ] QUICKSTART.md fourni
- [ ] COMPLIANCE.md fourni
- [ ] CAHIER_DES_CHARGES_VERIFICATION.md fourni

---

## 🐛 DÉPANNAGE RAPIDE

### Le chat ne se connecte pas
```bash
# Vérifier que daphne est en tête de INSTALLED_APPS
grep "daphne" config/settings.py | head -1
# Doit afficher: "daphne",
```

### Les messages ne s'affichent pas
- F12 → Network tab → chercher `ws://`
- WebSocket status doit être `101 (Switching Protocols)`

### API 404
```bash
# Vérifier les URLs
python manage.py show_urls | grep support
```

### SQLite permission error
```bash
# Réinitialiser la base
rm db.sqlite3
python manage.py migrate
python manage.py seed_db
```

---

## 📞 Points de Contact API

### Authentification
- **POST** `/api/auth/token/` → JWT token

### Support Client
- **GET** `/api/support/conversations/` → Lister
- **POST** `/api/support/conversations/` → Créer (client)
- **GET** `/api/support/conversations/{id}/` → Détail
- **WS** `/ws/chat/{id}/` → WebSocket

### Microcrédits
- **GET** `/api/microcredits/` → Lister
- **POST** `/api/microcredits/` → Créer

### Remboursements
- **GET** `/api/repayments/` → Lister

### Assurance
- **GET** `/api/insurance/` → Produits
- **GET** `/api/insurance/subscriptions/` → Souscriptions

### Notifications
- **GET** `/api/notifications/` → Lister

---

## 🚀 PRÊT POUR PRODUCTION

Une fois les tests validés :

1. **Configuration PostgreSQL**:
   ```bash
   set DB_ENGINE=django.db.backends.postgresql
   set DB_NAME=cofinance
   set DB_USER=postgres
   set DB_PASSWORD=<password>
   set DB_HOST=localhost
   set DB_PORT=5432
   ```

2. **Installer psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```

3. **Migrer vers PostgreSQL**:
   ```bash
   python manage.py migrate
   python manage.py seed_db
   ```

4. **Déployer sur serveur production** avec Gunicorn + Nginx

---

**Date**: 9 Juin 2026  
**Status**: ✅ **PRÊT POUR TEST ET VALIDATION**
