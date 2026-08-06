import os
import sys
from datetime import datetime
from typing import Optional

import sentry_sdk
import typer
from sqlalchemy.orm import Session

from epicevents.dao import ClientDAO, CollaborateurDAO, ContratDAO, EvenementDAO
from epicevents.database import engine
from epicevents.auth import AuthenticationError, authenticate, generate_auth_token, save_token, delete_token
from epicevents.permissions import AuthorizationError
from epicevents.clients import list_clients, create_client, update_client
from epicevents.contrats import (
    list_contracts,
    list_unsigned_contracts,
    list_unpaid_contracts,
    create_contract,
    update_contract,
)
from epicevents.evenements import (
    list_events,
    list_events_without_support,
    list_my_events,
    create_event,
    assign_support,
    update_event,
)
from epicevents.collaborateurs import create_collaborateur, update_collaborateur, delete_collaborateur

sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), send_default_pii=False)

session = Session(engine)
app = typer.Typer()


@app.command()
def login(email: str, password: str = typer.Option(..., prompt=True, hide_input=True)):
    """
    Authentifie un utilisateur avec son email et son mot de passe.
    """
    try:
        user = authenticate(session, email, password)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    token = generate_auth_token(user)
    save_token(token)

    typer.echo(f"Authentification de l'utilisateur avec l'email: {email}")


@app.command()
def logout():
    """
    Déconnecte l'utilisateur courant (supprime le jeton stocké).
    """

    delete_token()
    typer.echo("Déconnexion réussie.")


# --- Clients ---


@app.command("list-clients")
def cmd_list_clients():
    """
    Affiche tous les clients.
    """
    try:
        clients = list_clients(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    typer.echo("Liste des clients affichée.")
    for client in clients:
        typer.echo(f"ID: {client.id}, Nom: {client.nom}, Email: {client.email}")
        typer.echo(f"Téléphone: {client.telephone}, Entreprise: {client.nom_entreprise}")


@app.command("create-client")
def cmd_create_client(nom: str, email: str, telephone: str, nom_entreprise: str):
    """
    Crée un client (commercial uniquement, auto-association).
    """
    try:
        create_client(session, nom, email, telephone, nom_entreprise)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)
    typer.echo("Client créé avec succès.")


@app.command("update-client")
def cmd_update_client(
    client_id: int,
    nom: Optional[str] = None,
    email: Optional[str] = None,
    telephone: Optional[str] = None,
    nom_entreprise: Optional[str] = None,
):
    """
    Modifie un client (commercial responsable uniquement).
    """

    if not any([nom, email, telephone, nom_entreprise]):
        typer.echo("Aucun champ à mettre à jour fourni.")
        raise typer.Exit(code=1)

    try:
        client_instance = session.query(ClientDAO(session).model).get(client_id)
        if not client_instance:
            typer.echo(f"Client avec l'id {client_id} introuvable.")
            raise typer.Exit(code=1)

        nouv_nom = nom if nom is not None else client_instance.nom
        nouv_email = email if email is not None else client_instance.email
        nouv_telephone = telephone if telephone is not None else client_instance.telephone
        nouv_nom_entreprise = nom_entreprise if nom_entreprise is not None else client_instance.nom_entreprise

        kwargs = {
            "nom": nouv_nom,
            "email": nouv_email,
            "telephone": nouv_telephone,
            "nom_entreprise": nouv_nom_entreprise,
        }

        update_client(session, client_instance, **kwargs)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)
    typer.echo("Client mis à jour avec succès.")


# --- Contrats ---


@app.command("list-contracts")
def cmd_list_contracts():
    """
    Affiche tous les contrats.
    """
    try:
        contracts = list_contracts(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    typer.echo("Liste des contrats affichée.")
    for contract in contracts:
        typer.echo(f"ID: {contract.id}, Montant: {contract.montant}, Client: {contract.client_id}")


@app.command("list-unsigned-contracts")
def cmd_list_unsigned_contracts():
    """
    Affiche les contrats non signés.
    """
    try:
        unsigned_contracts = list_unsigned_contracts(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    typer.echo("Liste des contrats non signés affichée.")
    for contract in unsigned_contracts:
        typer.echo(f"ID: {contract.id}, Montant: {contract.montant}, Client: {contract.client_id}")


@app.command("list-unpaid-contracts")
def cmd_list_unpaid_contracts():
    """
    Affiche les contrats non soldés.
    """
    try:
        unpaid_contracts = list_unpaid_contracts(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    typer.echo("Liste des contrats non soldés affichée.")
    for contract in unpaid_contracts:
        typer.echo(f"ID: {contract.id}, Montant: {contract.montant}, Client: {contract.client_id}")


@app.command("create-contract")
def cmd_create_contract(montant: float, client_id: int):
    """
    Crée un contrat (gestion uniquement).
    """
    try:
        new_contract = create_contract(session, montant, client_id)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(
        f"Contrat créé avec succès. ID: {new_contract.id}, Montant: {new_contract.montant}, "
        f"Client: {new_contract.client_id}"
    )


@app.command("update-contract")
def cmd_update_contract(
    contract_id: int,
    montant: Optional[float] = None,
    montant_restant: Optional[float] = None,
    statut: Optional[bool] = None,
):
    """
    Modifie un contrat (gestion : tous ; commercial : ses clients uniquement).
    """

    if montant is None and montant_restant is None and statut is None:
        typer.echo("Aucun champ à mettre à jour fourni.")
        raise typer.Exit(code=1)

    try:
        contract_instance = session.query(ContratDAO(session).model).get(contract_id)
        if not contract_instance:
            typer.echo(f"Contrat avec l'id {contract_id} introuvable.")
            raise typer.Exit(code=1)

        nouv_montant = montant if montant is not None else contract_instance.montant
        nouv_montant_restant = montant_restant if montant_restant is not None else contract_instance.montant_restant
        nouv_statut = statut if statut is not None else contract_instance.statut

        kwargs = {
            "montant": nouv_montant,
            "montant_restant": nouv_montant_restant,
            "statut": nouv_statut,
        }

        updated_contract = update_contract(session, contract_instance, **kwargs)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(
        f"Contrat mis à jour avec succès. ID: {updated_contract.id}, Montant: {updated_contract.montant}, "
        f"Client: {updated_contract.client_id}"
    )


# --- Événements ---


@app.command("list-events")
def cmd_list_events():
    """
    Affiche tous les événements.
    """
    try:
        events = list_events(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    for event in events:
        typer.echo(f"Événement: {event.id}, Lieu: {event.location}, Début: {event.date_debut}")


@app.command("list-events-without-support")
def cmd_list_events_without_support():
    """
    Affiche les événements sans support assigné.
    """
    try:
        events = list_events_without_support(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    for event in events:
        typer.echo(f"Événement: {event.id}, Lieu: {event.location}, Début: {event.date_debut}")


@app.command("list-my-events")
def cmd_list_my_events():
    """
    Affiche les événements dont je suis le support.
    """
    try:
        events = list_my_events(session)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)

    for event in events:
        typer.echo(f"Événement: {event.id}, Lieu: {event.location}, Début: {event.date_debut}")


@app.command("create-event")
def cmd_create_event(
    date_debut: datetime,
    date_fin: datetime,
    location: str,
    attendees: int,
    contrat_id: int,
    notes: Optional[str] = None,
):
    """
    Crée un événement (commercial, si le contrat est signé).
    """
    try:
        event = create_event(session, date_debut, date_fin, location, attendees, notes, contrat_id)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Événement créé avec succès. ID: {event.id}, Lieu: {event.location}, Début: {event.date_debut}")


@app.command("assign-support")
def cmd_assign_support(event_id: int, support_id: int):
    """
    Assigne un support à un événement (gestion uniquement).
    """
    try:
        assign_support(session, event_id, support_id)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Support avec l'ID {support_id} assigné à l'événement avec l'ID {event_id}.")


@app.command("update-event")
def cmd_update_event(
    event_id: int,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
    location: Optional[str] = None,
    attendees: Optional[int] = None,
    notes: Optional[str] = None,
):
    """
    Modifie un événement (support responsable uniquement).
    """

    if not any([date_debut, date_fin, location, attendees, notes]):
        typer.echo("Aucun champ à mettre à jour fourni.")
        raise typer.Exit(code=1)

    try:
        event_instance = session.query(EvenementDAO(session).model).get(event_id)
        if not event_instance:
            typer.echo(f"Événement avec l'id {event_id} introuvable.")
            raise typer.Exit(code=1)

        nouv_date_debut = date_debut if date_debut is not None else event_instance.date_debut
        nouv_date_fin = date_fin if date_fin is not None else event_instance.date_fin
        nouv_location = location if location is not None else event_instance.location
        nouv_attendees = attendees if attendees is not None else event_instance.attendees
        nouv_notes = notes if notes is not None else event_instance.notes

        kwargs = {
            "date_debut": nouv_date_debut,
            "date_fin": nouv_date_fin,
            "location": nouv_location,
            "attendees": nouv_attendees,
            "notes": nouv_notes,
        }

        update_event(session, event_instance, **kwargs)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Événement mis à jour avec succès. ID: {event_id}")


# --- Collaborateurs ---


@app.command("create-collaborateur")
def cmd_create_collaborateur(
    numero_employe: str,
    nom: str,
    email: str,
    role_id: int,
    mot_de_passe: str = typer.Option(..., prompt=True, hide_input=True),
):
    """
    Crée un collaborateur (gestion uniquement).
    """
    try:
        new_collab = create_collaborateur(session, numero_employe, nom, email, mot_de_passe, role_id)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(
        f"Collaborateur créé avec succès. ID: {new_collab.id}, Nom: {new_collab.nom}, " f"Email: {new_collab.email}"
    )


@app.command("update-collaborateur")
def cmd_update_collaborateur(
    collaborateur_id: int,
    nom: Optional[str] = None,
    email: Optional[str] = None,
    role_id: Optional[int] = None,
):
    """
    Modifie un collaborateur (gestion uniquement).
    """

    if not any([nom, email, role_id]):
        typer.echo("Aucun champ à mettre à jour fourni.")
        raise typer.Exit(code=1)

    try:
        collaborateur_instance = session.query(CollaborateurDAO(session).model).get(collaborateur_id)
        if not collaborateur_instance:
            typer.echo(f"Collaborateur avec l'id {collaborateur_id} introuvable.")
            raise typer.Exit(code=1)

        nouv_nom = nom if nom is not None else collaborateur_instance.nom
        nouv_email = email if email is not None else collaborateur_instance.email
        nouv_role_id = role_id if role_id is not None else collaborateur_instance.role_id

        kwargs = {
            "nom": nouv_nom,
            "email": nouv_email,
            "role_id": nouv_role_id,
        }

        updated_collab = update_collaborateur(session, collaborateur_instance, **kwargs)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur de validation: {e}")
        raise typer.Exit(code=1)

    typer.echo(
        f"Collaborateur mis à jour avec succès. ID: {updated_collab.id}, Nom: {updated_collab.nom}, "
        f"Email: {updated_collab.email}"
    )


@app.command("delete-collaborateur")
def cmd_delete_collaborateur(collaborateur_id: int):
    """
    Supprime un collaborateur (gestion uniquement).
    """
    try:
        collaborateur_instance = session.query(CollaborateurDAO(session).model).get(collaborateur_id)
        if not collaborateur_instance:
            typer.echo(f"Collaborateur avec l'id {collaborateur_id} introuvable.")
            raise typer.Exit(code=1)

        delete_collaborateur(session, collaborateur_instance)
    except AuthenticationError as e:
        typer.echo(f"Erreur d'authentification: {e}")
        raise typer.Exit(code=1)
    except AuthorizationError as e:
        typer.echo(f"Erreur d'autorisation: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Erreur: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Collaborateur {collaborateur_id} supprimé avec succès.")


if __name__ == "__main__":
    try:
        exit_code = app(standalone_mode=False)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.flush(timeout=3)
        raise
    sys.exit(exit_code or 0)
