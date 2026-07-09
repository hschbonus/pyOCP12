from datetime import date

from epicevents.dao import ClientDAO
from epicevents.auth import get_current_user
from epicevents.permissions import AuthorizationError, require_role
from epicevents.validation import validate_email, validate_not_empty


def list_clients(session):
    get_current_user(session)
    return ClientDAO(session).list_all()


def create_client(session, nom, email, telephone, nom_entreprise):
    current_user = get_current_user(session)
    require_role(current_user, "commercial")
    validate_not_empty(nom, "nom")
    validate_not_empty(nom_entreprise, "nom_entreprise")
    validate_email(email)

    new_client = ClientDAO(session).create(
        nom=nom,
        email=email,
        telephone=telephone,
        nom_entreprise=nom_entreprise,
        date_creation=date.today(),
        date_maj=date.today(),
        commercial_id=current_user.id
    )
    return new_client


def update_client(session, instance, **kwargs):
    current_user = get_current_user(session)
    require_role(current_user, "commercial")

    client = ClientDAO(session).get_by_id(instance.id)

    if not client:
        raise ValueError(f"Client avec l'id {instance.id} introuvable.")

    if not current_user.id == client.commercial_id:
        raise AuthorizationError("Vous n'avez pas la permission de modifier ce client.")
    else:
        kwargs["date_maj"] = date.today()
        updated_client = ClientDAO(session).update(client, **kwargs)
    return updated_client
