import argparse
import sys

from sqlalchemy.orm import Session

from epicevents.database import engine
from epicevents.dao import RoleDAO, CollaborateurDAO
from epicevents.security import hash_password

ROLES = ["commercial", "support", "gestion"]


def ensure_roles(session: Session) -> None:
    role_dao = RoleDAO(session)
    for nom in ROLES:
        if not role_dao.get_by_nom(nom):
            role_dao.create(nom=nom)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap : cree les roles (commercial/support/gestion) "
        "et un premier collaborateur du departement gestion."
    )
    parser.add_argument("--numero-employe", required=True)
    parser.add_argument("--nom", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--mot-de-passe", required=True)
    args = parser.parse_args()

    with Session(engine) as session:
        ensure_roles(session)

        collaborateur_dao = CollaborateurDAO(session)
        if collaborateur_dao.get_by_email(args.email):
            print(f"Un collaborateur avec l'email {args.email} existe deja.")
            sys.exit(1)

        gestion_role = RoleDAO(session).get_by_nom("gestion")

        collaborateur_dao.create(
            numero_employe=args.numero_employe,
            nom=args.nom,
            email=args.email,
            mot_de_passe=hash_password(args.mot_de_passe),
            role_id=gestion_role.id,
        )
        print(f"Collaborateur '{args.nom}' cree avec le role gestion.")


if __name__ == "__main__":
    main()
