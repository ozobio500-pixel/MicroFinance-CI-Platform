import sys
import os
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta

# Initialiser Django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from microcredits.models import CreditApplication
from repayments.models import RepaymentInstallment
from insurance.models import InsuranceProduct, InsuranceSubscription
from support.models import Conversation, Message
from notifications.models import Notification
from rest_framework.test import APIClient

User = get_user_model()

def run_tests():
    print("=== DEBUT DES TESTS API ===")
    client = APIClient()

    # 1. Login Client
    print("\n[1] Connexion du Client (client1)...")
    res = client.post("/api/auth/token/", {"username": "client1", "password": "demo1234"})
    if res.status_code != 200:
        print(f"[FAIL] Echec de la connexion du client: {res.status_code}")
        return
    client_token = res.data["access"]
    print("[OK] Connexion client reussie.")

    # 2. Get Profile
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {client_token}")
    print("\n[2] Recuperation du profil...")
    res = client.get("/api/accounts/me/")
    if res.status_code != 200:
        print(f"[FAIL] Echec de recuperation du profil: {res.data}")
        return
    print(f"[OK] Profil recupere: {res.data['username']} (Score: {res.data.get('credit_score')})")

    # 3. Submit Credit Application
    print("\n[3] Soumission d'une demande de microcredit...")
    res = client.post("/api/microcredits/applications/", {"amount": 250000, "duration_months": 6})
    if res.status_code != 201:
        print(f"[FAIL] Echec de la demande de credit: {res.data}")
        return
    app_id = res.data["id"]
    print(f"[OK] Demande de credit soumise avec succes (ID: {app_id}, Score d'eligibilite: {res.data['eligibility_score']})")

    # 4. Connexion Agent
    print("\n[4] Connexion de l'Agent (agent1)...")
    client.credentials()  # clear auth
    res = client.post("/api/auth/token/", {"username": "agent1", "password": "demo1234"})
    if res.status_code != 200:
        print(f"[FAIL] Echec de la connexion de l'agent: {res.status_code}")
        return
    agent_token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {agent_token}")
    print("[OK] Connexion agent reussie.")

    # 5. Agent Workflow Transition (submitted -> in_review -> approved -> disbursed)
    print("\n[5] Transition du workflow de credit par l'Agent...")
    res = client.patch(f"/api/microcredits/applications/{app_id}/status/", {"status": "in_review"})
    if res.status_code != 200:
        print(f"[FAIL] Echec transition in_review: {res.data}")
        return
    print("[OK] Passage a 'En analyse' reussi.")

    res = client.patch(f"/api/microcredits/applications/{app_id}/status/", {"status": "approved"})
    if res.status_code != 200:
        print(f"[FAIL] Echec transition approved: {res.data}")
        return
    print("[OK] Passage a 'Approuvee' reussi.")

    res = client.patch(f"/api/microcredits/applications/{app_id}/status/", {"status": "disbursed"})
    if res.status_code != 200:
        print(f"[FAIL] Echec transition disbursed: {res.data}")
        return
    print("[OK] Passage a 'Decaissee' reussi.")

    # 6. Verify Installment creation
    print("\n[6] Verification des echeances de remboursement...")
    insts = RepaymentInstallment.objects.filter(application_id=app_id)
    if not insts.exists():
        print("[FAIL] Aucune echeance creee !")
        return
    print(f"[OK] {insts.count()} echeances creees avec succes.")
    first_inst = insts.first()
    print(f"   Mensualite 1: Du={first_inst.total_due} FCFA (Principal={first_inst.principal_amount}, Interet={first_inst.interest_amount}), Limite={first_inst.due_date}")

    # 7. Record Payment
    print("\n[7] Enregistrement d'un remboursement par l'agent...")
    res = client.post(f"/api/repayments/installments/{first_inst.id}/pay/", {"amount": int(first_inst.total_due)})
    if res.status_code != 200:
        print(f"[FAIL] Echec enregistrement paiement: {res.data}")
        return
    print(f"[OK] Paiement enregistre. Statut: {res.data['status']}, Solde du: {res.data['amount_paid']}/{res.data['total_due']}")

    # 8. Insurance Subscribe
    print("\n[8] Test d'assurance mobile...")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {client_token}") # Back to client
    res = client.get("/api/insurance/products/")
    if res.status_code != 200 or not res.data:
        print(f"[FAIL] Echec catalogue assurances: {res.data}")
        return
    prod_id = res.data[0]["id"]
    print(f"[OK] Produits trouves: {len(res.data)}. Souscription au produit ID: {prod_id}")
    
    res = client.post("/api/insurance/subscribe/", {"product_id": prod_id})
    if res.status_code != 201:
        print(f"[FAIL] Echec souscription assurance: {res.data}")
        return
    print(f"[OK] Souscription reussie (No Police: {res.data['policy_number']}, Fin: {res.data['end_date']})")

    # 9. Support Conversations & Chat
    print("\n[9] Test du support chat...")
    res = client.post("/api/support/conversations/", {"subject": "Question remboursement"})
    if res.status_code != 201:
        print(f"[FAIL] Echec creation conversation: {res.data}")
        return
    conv_id = res.data["id"]
    print(f"[OK] Conversation creee (ID: {conv_id}, Agent: {res.data['assigned_agent_username']})")

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {agent_token}") # agent
    res = client.post("/api/support/conversations/", {"subject": "Contact client", "client_username": "client1"})
    if res.status_code != 201:
        print(f"[FAIL] Echec creation conv par agent: {res.data}")
        return
    agent_conv_id = res.data["id"]
    print(f"[OK] Conversation creee par agent (ID: {agent_conv_id})")

    res = client.delete(f"/api/support/conversations/{agent_conv_id}/")
    if res.status_code != 204:
        print(f"[FAIL] Echec suppression conv: {res.status_code}")
        return
    print("[OK] Suppression reussie.")

    # 10. Dashboard KPIs
    print("\n[10] Verification du Dashboard Admin...")
    client.credentials()  # clear auth
    res = client.post("/api/auth/token/", {"username": "admin", "password": "demo1234"})
    admin_token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    res = client.get("/api/dashboard/kpis/")
    if res.status_code != 200:
        print(f"[FAIL] Echec du dashboard: {res.data}")
        return
    print(f"[OK] Donnees dashboard recuperees:")
    print(f"   Recouvrement: {res.data['recovery_rate_percent']}%")
    print(f"   Assurances: {res.data['active_insurance_subscriptions']}")
    print(f"   Chats: {res.data['open_support_conversations']}")
    print(f"   Credits: {res.data['total_credit_requests']}")

    print("\n=== TOUS LES TESTS API ONT REUSSI ! ===")

if __name__ == "__main__":
    run_tests()
