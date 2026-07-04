from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, date
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    nom: Mapped[str]


class Collaborateur(Base):
    __tablename__ = "collaborateurs"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    numero_employe: Mapped[str] = mapped_column(unique=True)
    nom: Mapped[str]
    email: Mapped[str]
    mot_de_passe: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    nom: Mapped[str]
    email: Mapped[str]
    telephone: Mapped[str]
    nom_entreprise: Mapped[str]
    date_creation: Mapped[date]
    date_maj: Mapped[date]
    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborateurs.id"))


class Contrat(Base):
    __tablename__ = "contrats"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    montant: Mapped[Decimal]
    montant_restant: Mapped[Decimal]
    date: Mapped[date]
    statut: Mapped[bool]
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))


class Evenement(Base):
    __tablename__ = "evenements"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    date_debut: Mapped[datetime]
    date_fin: Mapped[datetime]
    location: Mapped[str]
    attendees: Mapped[int]
    notes: Mapped[Optional[str]] = mapped_column(Text)
    contrat_id: Mapped[int] = mapped_column(ForeignKey("contrats.id"), unique=True)
    support_id: Mapped[Optional[int]] = mapped_column(ForeignKey("collaborateurs.id"))
