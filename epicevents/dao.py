from typing import Generic, TypeVar, Type, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from epicevents.models import Base, Collaborateur, Client, Contrat, Evenement

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


class CollaborateurDAO(BaseDAO[Collaborateur]):
    model = Collaborateur


class ClientDAO(BaseDAO[Client]):
    model = Client


class ContratDAO(BaseDAO[Contrat]):
    model = Contrat


class EvenementDAO(BaseDAO[Evenement]):
    model = Evenement
