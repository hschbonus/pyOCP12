import pytest

from epicevents.collaborateurs import create_collaborateur, update_collaborateur
from epicevents.permissions import AuthorizationError
from epicevents.models import Role


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
