from datetime import datetime


def validate_email(email: str) -> None:
    if "@" not in email:
        raise ValueError(f"L'adresse e-mail '{email}' n'est pas valide.")


def validate_not_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"Le champ '{field_name}' ne peut pas être vide.")


def validate_positive(value, field_name: str) -> None:
    if value <= 0:
        raise ValueError(f"Le champ '{field_name}' doit être un nombre positif.")


def validate_dates_order(date_debut: datetime, date_fin: datetime) -> None:
    if date_debut >= date_fin:
        raise ValueError("La date de début doit être antérieure à la date de fin.")
