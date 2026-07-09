from epicevents.auth import get_current_user
from epicevents.dao import CollaborateurDAO, ContratDAO, EvenementDAO
from epicevents.permissions import AuthorizationError, require_role
from epicevents.validation import validate_dates_order, validate_not_empty, validate_positive


def list_events(session):
    get_current_user(session)
    return EvenementDAO(session).list_all()


def list_events_without_support(session):
    get_current_user(session)
    return EvenementDAO(session).list_without_support()


def list_my_events(session):
    user = get_current_user(session)
    return EvenementDAO(session).list_by_support(user.id)


def create_event(session, date_debut, date_fin, location, attendees, notes, contrat_id):
    current_user = get_current_user(session)
    require_role(current_user, "commercial")
    validate_not_empty(location, "location")
    validate_positive(attendees, "attendees")
    validate_dates_order(date_debut, date_fin)

    contrat = ContratDAO(session).get_by_id(contrat_id)
    if not contrat:
        raise ValueError(f"Contrat avec l'id {contrat_id} introuvable.")

    if contrat.client.commercial_id != current_user.id:
        raise AuthorizationError("Ce contrat n'appartient pas à l'un de vos clients.")

    if contrat.statut is not True:
        raise ValueError(f"Le contrat avec l'id {contrat_id} n'est pas signé, impossible de créer un événement.")

    new_event = EvenementDAO(session).create(
        date_debut=date_debut,
        date_fin=date_fin,
        location=location,
        attendees=attendees,
        notes=notes,
        contrat_id=contrat_id,
        support_id=None
    )
    return new_event


def assign_support(session, event_id, support_id):
    current_user = get_current_user(session)
    require_role(current_user, "gestion")

    event = EvenementDAO(session).get_by_id(event_id)
    if not event:
        raise ValueError(f"Événement avec l'id {event_id} introuvable.")

    support = CollaborateurDAO(session).get_by_id(support_id)
    if not support:
        raise ValueError(f"Collaborateur avec l'id {support_id} introuvable.")

    if support.role.nom != "support":
        raise ValueError(f"Le collaborateur avec l'id {support_id} n'est pas un support.")

    updated_event = EvenementDAO(session).update(event, support_id=support_id)
    return updated_event


def update_event(session, instance, **kwargs):
    current_user = get_current_user(session)
    require_role(current_user, "support")

    event = EvenementDAO(session).get_by_id(instance.id)
    if not event:
        raise ValueError(f"Événement avec l'id {instance.id} introuvable.")

    if event.support_id != current_user.id:
        raise AuthorizationError("Vous n'avez pas la permission de modifier cet événement.")

    updated_event = EvenementDAO(session).update(event, **kwargs)
    return updated_event
