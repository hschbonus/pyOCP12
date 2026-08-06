import sentry_sdk
from sqlalchemy.exc import IntegrityError

from epicevents.dao import CollaborateurDAO, EvenementDAO
from epicevents.security import hash_password
from epicevents.auth import get_current_user
from epicevents.permissions import require_role
from epicevents.validation import validate_email, validate_not_empty


def create_collaborateur(session, numero_employe, nom, email, mot_de_passe, role_id):
    require_role(get_current_user(session), "gestion")
    validate_not_empty(numero_employe, "numero_employe")
    validate_not_empty(nom, "nom")
    validate_email(email)

    try:
        new_collab = CollaborateurDAO(session).create(
            numero_employe=numero_employe,
            nom=nom,
            email=email,
            mot_de_passe=hash_password(mot_de_passe),
            role_id=role_id,
        )
    except IntegrityError:
        session.rollback()
        raise ValueError(f"Un collaborateur avec l'email « {email} » ou le numéro « {numero_employe} » existe déjà.")

    message = (
        f"Collaborateur créé avec succès. ID: {new_collab.id}, Nom: {new_collab.nom}, " f"Email: {new_collab.email}"
    )
    sentry_sdk.capture_message(message, level="info")

    return new_collab


def update_collaborateur(session, instance, **kwargs):
    require_role(get_current_user(session), "gestion")
    validate_not_empty(kwargs.get("nom"), "nom")
    validate_email(kwargs.get("email"))

    collaborateur = CollaborateurDAO(session).get_by_id(instance.id)
    if not collaborateur:
        raise ValueError(f"Collaborateur avec l'id {instance.id} introuvable.")
    else:
        if "mot_de_passe" in kwargs and kwargs["mot_de_passe"]:
            kwargs["mot_de_passe"] = hash_password(kwargs["mot_de_passe"])
        try:
            updated_collab = CollaborateurDAO(session).update(collaborateur, **kwargs)
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Un collaborateur avec l'email « {kwargs.get('email')} » existe déjà.")

    message = (
        f"Collaborateur mis à jour avec succès. ID: {updated_collab.id}, Nom: {updated_collab.nom}, "
        f"Email: {updated_collab.email}"
    )

    sentry_sdk.capture_message(message, level="info")

    return updated_collab


def delete_collaborateur(session, instance):
    require_role(get_current_user(session), "gestion")

    collaborateur = CollaborateurDAO(session).get_by_id(instance.id)
    if not collaborateur:
        raise ValueError(f"Collaborateur avec l'id {instance.id} introuvable.")

    if EvenementDAO(session).list_by_support(collaborateur.id):
        raise ValueError(
            "Impossible de supprimer ce collaborateur : il est encore assigné "
            "à au moins un événement en tant que support."
        )

    try:
        CollaborateurDAO(session).delete(collaborateur)
    except IntegrityError:
        session.rollback()
        raise ValueError(
            "Impossible de supprimer ce collaborateur : il est encore référencé "
            "par au moins un client ou événement."
        )

    sentry_sdk.capture_message(f"Collaborateur supprimé. ID: {instance.id}", level="info")
