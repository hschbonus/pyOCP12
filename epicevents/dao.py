from typing import Generic, TypeVar, Type, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from epicevents.models import Base, Role, Collaborateur, Client, Contrat, Evenement

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def list_all(self) -> list[ModelType]:
        return self.session.scalars(select(self.model)).all()

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.session.commit()
        return instance

    def delete(self, instance: ModelType) -> None:
        self.session.delete(instance)
        self.session.commit()


class RoleDAO(BaseDAO[Role]):
    model = Role

    def get_by_nom(self, nom: str) -> Optional[Role]:
        return self.session.scalars(select(Role).where(Role.nom == nom)).first()


class CollaborateurDAO(BaseDAO[Collaborateur]):
    model = Collaborateur

    def get_by_email(self, email: str) -> Optional[Collaborateur]:
        return self.session.scalars(select(Collaborateur).where(Collaborateur.email == email)).first()


class ClientDAO(BaseDAO[Client]):
    model = Client


class ContratDAO(BaseDAO[Contrat]):
    model = Contrat

    def list_unsigned(self) -> list[Contrat]:
        return self.session.scalars(
            select(Contrat).where(Contrat.statut.is_(False))
        ).all()

    def list_unpaid(self) -> list[Contrat]:
        return self.session.scalars(
            select(Contrat).where(Contrat.montant_restant > 0)
        ).all()


class EvenementDAO(BaseDAO[Evenement]):
    model = Evenement

    def list_without_support(self) -> list[Evenement]:
        return self.session.scalars(
            select(Evenement).where(Evenement.support_id.is_(None))
        ).all()

    def list_by_support(self, support_id: int) -> list[Evenement]:
        return self.session.scalars(
            select(Evenement).where(Evenement.support_id == support_id)
        ).all()
