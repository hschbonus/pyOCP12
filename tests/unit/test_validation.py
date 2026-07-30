from datetime import datetime

import pytest

from epicevents import validation


# Test qu'un email valide ne lève aucune exception
def test_validate_email_valide():
    validation.validate_email("test@example.com")


# Test qu'un email sans @ lève ValueError
def test_validate_email_invalide():
    with pytest.raises(ValueError):
        validation.validate_email("pas-un-email")


# Test qu'une chaîne non vide ne lève aucune exception
def test_validate_not_empty_valide():
    validation.validate_not_empty("valeur", "champ")


# Test qu'une chaîne vide (ou espaces uniquement) lève ValueError
def test_validate_not_empty_invalide():
    with pytest.raises(ValueError):
        validation.validate_not_empty("   ", "champ")


# Test qu'un nombre positif ne lève aucune exception
def test_validate_positive_valide():
    validation.validate_positive(10, "montant")


# Test qu'un nombre négatif ou nul lève ValueError
def test_validate_positive_invalide():
    with pytest.raises(ValueError):
        validation.validate_positive(-5, "montant")


# Test que date_debut < date_fin ne lève aucune exception
def test_validate_dates_order_valide():
    validation.validate_dates_order(datetime(2026, 1, 1), datetime(2026, 1, 2))


# Test que date_debut >= date_fin lève ValueError
def test_validate_dates_order_invalide():
    with pytest.raises(ValueError):
        validation.validate_dates_order(datetime(2026, 1, 2), datetime(2026, 1, 1))
