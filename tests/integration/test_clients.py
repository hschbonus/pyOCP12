import pytest

from epicevents.clients import create_client, update_client, list_clients
from epicevents.permissions import AuthorizationError


# Test que list_clients renvoie bien tous les clients existants
def test_list_clients(session, make_current_user):
    make_current_user("commercial")
    create_client(session, "Client A", "a@test.local", "0600000001", "Entreprise A")
    create_client(session, "Client B", "b@test.local", "0600000002", "Entreprise B")

    result = list_clients(session)
    assert len(result) == 2


# Test qu'un commercial peut créer un client, auto-associé à lui
def test_create_client_succes(session, make_current_user):
    user = make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")
    assert client.commercial_id == user.id
    assert client.nom == "Client Test"


# Test qu'un non-commercial (ex: gestion) est refusé à la création
def test_create_client_role_refuse(session, make_current_user):
    make_current_user("gestion")
    with pytest.raises(AuthorizationError):
        create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")


# Test que le commercial propriétaire peut modifier son client
def test_update_client_succes(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    updated = update_client(
        session,
        client,
        nom="Nouveau Nom",
        email=client.email,
        telephone=client.telephone,
        nom_entreprise=client.nom_entreprise,
    )
    assert updated.nom == "Nouveau Nom"


# Test qu'un commercial non propriétaire est refusé à la modification
def test_update_client_pas_proprietaire(session, make_current_user):
    make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("commercial")
    with pytest.raises(AuthorizationError):
        update_client(
            session,
            client,
            nom="Hack",
            email=client.email,
            telephone=client.telephone,
            nom_entreprise=client.nom_entreprise,
        )
