from types import SimpleNamespace

import pytest

from epicevents import permissions


# Test qu'un collaborateur avec le bon rôle ne lève aucune exception
def test_require_role_autorise():
    collaborateur = SimpleNamespace(role=SimpleNamespace(nom="gestion"))
    permissions.require_role(collaborateur, "gestion", "commercial")


# Test qu'un collaborateur avec un rôle non autorisé lève AuthorizationError
def test_require_role_refuse():
    collaborateur = SimpleNamespace(role=SimpleNamespace(nom="support"))
    with pytest.raises(permissions.AuthorizationError):
        permissions.require_role(collaborateur, "gestion", "commercial")
