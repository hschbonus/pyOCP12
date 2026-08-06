from datetime import date, datetime

import pytest

from epicevents.collaborateurs import create_collaborateur, update_collaborateur, delete_collaborateur
from epicevents.dao import CollaborateurDAO
from epicevents.permissions import AuthorizationError
from epicevents.models import Role, Client, Contrat, Evenement


def _get_or_create_role(session, nom):
    role = session.query(Role).filter_by(nom=nom).first()
    if not role:
        role = Role(nom=nom)
        session.add(role)
        session.commit()
    return role


# Test que gestion peut créer un collaborateur, mot de passe haché en base
def test_create_collaborateur_succes(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")

    collab = create_collaborateur(
        session, "EMP999", "Nouveau Collab", "nouveau@test.local", "MotDePasse123", role_commercial.id
    )
    assert collab.nom == "Nouveau Collab"
    assert collab.mot_de_passe != "MotDePasse123"


# Test qu'un non-gestion est refusé à la création
def test_create_collaborateur_role_refuse(session, make_current_user):
    make_current_user("commercial")
    role_commercial = _get_or_create_role(session, "commercial")

    with pytest.raises(AuthorizationError):
        create_collaborateur(
            session, "EMP999", "Nouveau Collab", "nouveau@test.local", "MotDePasse123", role_commercial.id
        )


# Test que gestion peut modifier un collaborateur existant
def test_update_collaborateur_succes(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")
    collab = create_collaborateur(
        session, "EMP999", "Nouveau Collab", "nouveau@test.local", "MotDePasse123", role_commercial.id
    )

    updated = update_collaborateur(session, collab, nom="Collab Modifie", email=collab.email, role_id=collab.role_id)
    assert updated.nom == "Collab Modifie"


# Test que gestion peut supprimer un collaborateur non référencé
def test_delete_collaborateur_succes(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")
    collab = create_collaborateur(
        session, "EMP999", "A Supprimer", "asupprimer@test.local", "MotDePasse123", role_commercial.id
    )
    collab_id = collab.id

    delete_collaborateur(session, collab)

    assert CollaborateurDAO(session).get_by_id(collab_id) is None


# Test qu'un non-gestion est refusé à la suppression
def test_delete_collaborateur_role_refuse(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")
    collab = create_collaborateur(
        session, "EMP999", "A Supprimer", "asupprimer@test.local", "MotDePasse123", role_commercial.id
    )

    make_current_user("commercial")

    with pytest.raises(AuthorizationError):
        delete_collaborateur(session, collab)


# Test qu'un collaborateur introuvable lève une erreur claire
def test_delete_collaborateur_introuvable(session, make_current_user):
    make_current_user("gestion")

    class _FakeInstance:
        id = 999999

    with pytest.raises(ValueError):
        delete_collaborateur(session, _FakeInstance())


# Test qu'un commercial encore référencé par un client ne peut pas être supprimé
def test_delete_collaborateur_refuse_reference_client(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")
    commercial = create_collaborateur(
        session, "EMP999", "Commercial Occupe", "commercial-occupe@test.local", "MotDePasse123", role_commercial.id
    )

    client = Client(
        nom="Client Test",
        email="client-test@test.local",
        telephone="0000000000",
        nom_entreprise="Entreprise Test",
        date_creation=date.today(),
        date_maj=date.today(),
        commercial_id=commercial.id,
    )
    session.add(client)
    session.commit()

    with pytest.raises(ValueError):
        delete_collaborateur(session, commercial)


# Test qu'un support encore assigné à un événement ne peut pas être supprimé
def test_delete_collaborateur_refuse_reference_evenement(session, make_current_user):
    make_current_user("gestion")
    role_commercial = _get_or_create_role(session, "commercial")
    role_support = _get_or_create_role(session, "support")

    commercial = create_collaborateur(
        session, "EMP997", "Commercial Ref", "commercial-ref@test.local", "MotDePasse123", role_commercial.id
    )
    support = create_collaborateur(
        session, "EMP998", "Support Occupe", "support-occupe@test.local", "MotDePasse123", role_support.id
    )

    client = Client(
        nom="Client Test",
        email="client-test2@test.local",
        telephone="0000000000",
        nom_entreprise="Entreprise Test",
        date_creation=date.today(),
        date_maj=date.today(),
        commercial_id=commercial.id,
    )
    session.add(client)
    session.commit()

    contrat = Contrat(montant=1000, montant_restant=1000, date=date.today(), statut=True, client_id=client.id)
    session.add(contrat)
    session.commit()

    evenement = Evenement(
        date_debut=datetime.now(),
        date_fin=datetime.now(),
        location="Paris",
        attendees=10,
        contrat_id=contrat.id,
        support_id=support.id,
    )
    session.add(evenement)
    session.commit()

    with pytest.raises(ValueError):
        delete_collaborateur(session, support)
