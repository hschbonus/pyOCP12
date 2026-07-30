from datetime import datetime

import pytest

from epicevents.clients import create_client
from epicevents.contrats import create_contract, update_contract
from epicevents.evenements import (
    create_event,
    assign_support,
    update_event,
    list_events,
    list_events_without_support,
    list_my_events,
)
from epicevents.permissions import AuthorizationError


def _make_signed_contract(session, commercial, make_current_user, set_current_user):
    set_current_user(commercial)
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    contract = create_contract(session, 1000, client.id)
    contract = update_contract(session, contract, montant=1000, montant_restant=1000, statut=True)

    set_current_user(commercial)
    return contract


# Test que list_events renvoie bien tous les événements existants
def test_list_events(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    result = list_events(session)
    assert len(result) == 1


# Test que list_events_without_support ne renvoie que les événements sans support assigné
def test_list_events_without_support(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    result = list_events_without_support(session)
    assert len(result) == 1
    assert result[0].id == event.id


# Test que list_my_events ne renvoie que les événements assignés au support courant
def test_list_my_events(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    support = make_current_user("support")
    make_current_user("gestion")
    assign_support(session, event.id, support.id)

    set_current_user(support)
    result = list_my_events(session)
    assert len(result) == 1
    assert result[0].id == event.id


# Test qu'un commercial peut créer un événement sur un contrat signé de son client
def test_create_event_succes(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)

    event = create_event(
        session,
        datetime(2026, 9, 1, 14, 0),
        datetime(2026, 9, 1, 20, 0),
        "Salle Test",
        50,
        None,
        contract.id,
    )
    assert event.contrat_id == contract.id
    assert event.support_id is None


# Test qu'un contrat non signé refuse la création d'événement
def test_create_event_contrat_non_signe(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    client = create_client(session, "Client Test", "client@test.local", "0600000000", "Entreprise Test")

    make_current_user("gestion")
    contract = create_contract(session, 1000, client.id)  # non signé par défaut

    set_current_user(commercial)
    with pytest.raises(ValueError):
        create_event(
            session,
            datetime(2026, 9, 1, 14, 0),
            datetime(2026, 9, 1, 20, 0),
            "Salle Test",
            50,
            None,
            contract.id,
        )


# Test qu'un commercial non propriétaire du contrat est refusé
def test_create_event_pas_proprietaire(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)

    make_current_user("commercial")  # un autre commercial
    with pytest.raises(AuthorizationError):
        create_event(
            session,
            datetime(2026, 9, 1, 14, 0),
            datetime(2026, 9, 1, 20, 0),
            "Salle Test",
            50,
            None,
            contract.id,
        )


# Test que gestion peut assigner un support à un événement
def test_assign_support_succes(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    support = make_current_user("support")
    make_current_user("gestion")

    updated_event = assign_support(session, event.id, support.id)
    assert updated_event.support_id == support.id


# Test qu'assigner un collaborateur non-support est refusé
def test_assign_support_cible_non_support(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    autre_commercial = make_current_user("commercial")
    make_current_user("gestion")

    with pytest.raises(ValueError):
        assign_support(session, event.id, autre_commercial.id)


# Test que le support assigné peut modifier son événement
def test_update_event_succes(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    support = make_current_user("support")
    make_current_user("gestion")
    event = assign_support(session, event.id, support.id)

    set_current_user(support)
    updated = update_event(
        session,
        event,
        location="Nouvelle Salle",
        date_debut=event.date_debut,
        date_fin=event.date_fin,
        attendees=event.attendees,
        notes=event.notes,
    )
    assert updated.location == "Nouvelle Salle"


# Test qu'un support non assigné à l'événement est refusé
def test_update_event_pas_le_support_assigne(session, make_current_user, set_current_user):
    commercial = make_current_user("commercial")
    contract = _make_signed_contract(session, commercial, make_current_user, set_current_user)
    event = create_event(
        session, datetime(2026, 9, 1, 14, 0), datetime(2026, 9, 1, 20, 0), "Salle Test", 50, None, contract.id
    )

    support = make_current_user("support")
    make_current_user("gestion")
    event = assign_support(session, event.id, support.id)

    make_current_user("support")  # un autre support, non assigné
    with pytest.raises(AuthorizationError):
        update_event(
            session,
            event,
            location="Hack",
            date_debut=event.date_debut,
            date_fin=event.date_fin,
            attendees=event.attendees,
            notes=event.notes,
        )
