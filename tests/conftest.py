import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.pool import StaticPool

from epicevents.models import Base, Role, Collaborateur


@pytest.fixture
def session():
    """Session SQLAlchemy sur une base SQLite en mémoire, recréée à chaque test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with SQLAlchemySession(engine) as db_session:
        yield db_session


@pytest.fixture
def set_current_user(monkeypatch):
    """
    Fait en sorte que get_current_user(session) renvoie le collaborateur
    donné, sans jamais toucher au vrai fichier ~/.epicevents_token (on
    monkeypatch load_token/decode_auth_token dans le module auth,
    get_current_user appelle ces deux-là en interne).

    Utile pour "reconnecter" un collaborateur déjà créé (ex: repasser du
    point de vue de gestion à celui du commercial propriétaire).

    Usage dans un test : set_current_user(un_collaborateur_deja_cree)
    """

    def _set(collaborateur):
        monkeypatch.setattr("epicevents.auth.load_token", lambda: "fake-token")
        monkeypatch.setattr("epicevents.auth.decode_auth_token", lambda s, t: collaborateur)
        return collaborateur

    return _set


@pytest.fixture
def make_current_user(session, set_current_user):
    """
    Crée un nouveau collaborateur dans la base de test et le rend courant
    (via set_current_user).

    Usage dans un test : user = make_current_user("commercial")
    """
    compteur = {"n": 0}

    def _make(role_nom="commercial"):
        compteur["n"] += 1
        role = session.query(Role).filter_by(nom=role_nom).first()
        if not role:
            role = Role(nom=role_nom)
            session.add(role)
            session.commit()

        collaborateur = Collaborateur(
            numero_employe=f"EMP-TEST-{role_nom}-{compteur['n']}",
            nom="Test User",
            email=f"{role_nom}-{compteur['n']}@test.local",
            mot_de_passe="hash-non-utilise-en-test",
            role_id=role.id,
        )
        session.add(collaborateur)
        session.commit()

        return set_current_user(collaborateur)

    return _make
