import pytest

from epicevents.clients import create_client
from epicevents.contrats import (
    create_contract,
    update_contract,
    list_contracts,
    list_unsigned_contracts,
    list_unpaid_contracts,
)
from epicevents.permissions import AuthorizationError


# Test que list_contracts renvoie bien tous les contrats existants
def test_list_contracts(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    create_contract(session, 1000, client.id)
    create_contract(session, 2000, client.id)

    result = list_contracts(session)
    assert len(result) == 2


# Test que list_unsigned_contracts ne renvoie que les contrats non signés
def test_list_unsigned_contracts(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    non_signe = create_contract(session, 1000, client.id)
    signe = create_contract(session, 2000, client.id)
    update_contract(session, signe, montant=2000, montant_restant=2000, statut=True)

    result = list_unsigned_contracts(session)
    assert len(result) == 1
    assert result[0].id == non_signe.id


# Test que list_unpaid_contracts ne renvoie que les contrats avec un solde restant
def test_list_unpaid_contracts(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    solde = create_contract(session, 1000, client.id)
    update_contract(session, solde, montant=1000, montant_restant=0, statut=True)
    non_solde = create_contract(session, 2000, client.id)

    result = list_unpaid_contracts(session)
    assert len(result) == 1
    assert result[0].id == non_solde.id


# Test que gestion peut créer un contrat
def test_create_contract_succes(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    contract = create_contract(session, 1000, client.id)
    assert contract.client_id == client.id
    assert contract.statut is False
    assert contract.montant_restant == 1000


# Test qu'un non-gestion (ex: commercial) est refusé à la création
def test_create_contract_role_refuse(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    with pytest.raises(AuthorizationError):
        create_contract(session, 1000, client.id)


# Test que gestion ou le commercial propriétaire du client peut modifier
def test_update_contract_succes(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    contract = create_contract(session, 1000, client.id)

    set_current_user(commercial)
    updated = update_contract(session, contract, montant=2000, montant_restant=2000, statut=False)
    assert updated.montant == 2000


# Test qu'un commercial non propriétaire du client est refusé
def test_update_contract_pas_proprietaire(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    contract = create_contract(session, 1000, client.id)

    make_current_user("commercial")
    with pytest.raises(AuthorizationError):
        update_contract(session, contract, montant=2000, montant_restant=2000, statut=False)
