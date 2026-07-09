from epicevents.models import Collaborateur


class AuthorizationError(Exception):
    pass


def require_role(collaborateur: Collaborateur, *allowed_roles: str) -> None:
    if collaborateur.role.nom not in allowed_roles:
        raise AuthorizationError(f"Accès refusé : le rôle requis est l'un des suivants : {', '.join(allowed_roles)}")
