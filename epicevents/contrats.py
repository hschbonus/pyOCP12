from datetime import date

from epicevents.auth import get_current_user
from epicevents.dao import ContratDAO
from epicevents.permissions import AuthorizationError, require_role
from epicevents.validation import validate_positive


def list_contracts(session):
    get_current_user(session)
    return ContratDAO(session).list_all()


def list_unsigned_contracts(session):
    get_current_user(session)
    return ContratDAO(session).list_unsigned()


def list_unpaid_contracts(session):
    get_current_user(session)
    return ContratDAO(session).list_unpaid()


def create_contract(session, montant, client_id):
    require_role(get_current_user(session), "gestion")
    validate_positive(montant, "montant")

    new_contract = ContratDAO(session).create(
        montant=montant,
        montant_restant=montant,
        date=date.today(),
        statut=False,
        client_id=client_id
    )
    return new_contract


def update_contract(session, instance, **kwargs):
    current_user = get_current_user(session)
    require_role(current_user, "gestion", "commercial")

    if current_user.role.nom == "commercial" and instance.client.commercial_id != current_user.id:
        raise AuthorizationError("Vous n'avez pas la permission de modifier ce contrat.")

    contract = ContratDAO(session).get_by_id(instance.id)
    if not contract:
        raise ValueError(f"Contrat avec l'id {instance.id} introuvable.")
    return ContratDAO(session).update(contract, **kwargs)
