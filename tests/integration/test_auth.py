import pytest

from epicevents import auth
from epicevents.security import hash_password
from epicevents.models import Role, Collaborateur


def _make_collaborateur(session, email="user@test.local", mot_de_passe="MotDePasse123"):
    role = Role(nom="commercial")
    session.add(role)
    session.commit()

    collaborateur = Collaborateur(
        numero_employe="EMP-AUTH",
        nom="Auth Test",
        email=email,
        mot_de_passe=hash_password(mot_de_passe),
        role_id=role.id,
    )
    session.add(collaborateur)
    session.commit()
    return collaborateur


# Test qu'un email + mot de passe valides renvoient le bon collaborateur
def test_authenticate_succes(session):
    collaborateur = _make_collaborateur(session)
    result = auth.authenticate(session, collaborateur.email, "MotDePasse123")
    assert result.id == collaborateur.id


# Test qu'un mauvais mot de passe lève AuthenticationError
def test_authenticate_mot_de_passe_incorrect(session):
    collaborateur = _make_collaborateur(session)
    with pytest.raises(auth.AuthenticationError):
        auth.authenticate(session, collaborateur.email, "MauvaisMotDePasse")


# Test qu'un email inconnu lève AuthenticationError
def test_authenticate_email_inconnu(session):
    with pytest.raises(auth.AuthenticationError):
        auth.authenticate(session, "inconnu@test.local", "peu-importe")


# Test qu'un jeton généré puis décodé renvoie le bon collaborateur
def test_generate_and_decode_token(session):
    collaborateur = _make_collaborateur(session)
    token = auth.generate_auth_token(collaborateur)
    result = auth.decode_auth_token(session, token)
    assert result.id == collaborateur.id


# Test qu'un jeton invalide/corrompu lève AuthenticationError
def test_decode_token_invalide(session):
    with pytest.raises(auth.AuthenticationError):
        auth.decode_auth_token(session, "token-invalide")


# Test que get_current_user sans jeton stocké lève AuthenticationError
def test_get_current_user_sans_token(session, monkeypatch):
    monkeypatch.setattr(auth, "load_token", lambda: None)
    with pytest.raises(auth.AuthenticationError):
        auth.get_current_user(session)
