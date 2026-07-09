from epicevents.dao import CollaborateurDAO
from epicevents.models import Collaborateur
from epicevents.security import verify_password
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
import os
import jwt

load_dotenv()


class AuthenticationError(Exception):
    pass


def authenticate(session, email: str, mot_de_passe: str) -> Collaborateur:
    collaborateur = CollaborateurDAO(session).get_by_email(email)
    if collaborateur and verify_password(collaborateur.mot_de_passe, mot_de_passe):
        return collaborateur
    else:
        raise AuthenticationError("Identifiants invalides")


def generate_auth_token(collaborateur: Collaborateur) -> str:
    payload = {
        "id": collaborateur.id,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp())
    }
    token = jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")
    return token


def decode_auth_token(session, token: str) -> Collaborateur:
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
        collaborateur = CollaborateurDAO(session).get_by_id(payload["id"])
        if not collaborateur:
            raise AuthenticationError("Utilisateur non trouvé")
        return collaborateur
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Le token a expiré")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token invalide")


def save_token(token: str, filename: str = ".epicevents_token"):
    TOKEN_PATH = Path.home() / filename
    TOKEN_PATH.write_text(token)
    os.chmod(TOKEN_PATH, 0o600)


def load_token(filename: str = ".epicevents_token") -> Optional[str]:
    TOKEN_PATH = Path.home() / filename
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text()
    return None


def delete_token(filename: str = ".epicevents_token"):
    TOKEN_PATH = Path.home() / filename
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()


def get_current_user(session) -> Collaborateur:
    token = load_token()
    if token:
        return decode_auth_token(session, token)
    else:
        raise AuthenticationError("Aucun token trouvé. Veuillez vous connecter.")
