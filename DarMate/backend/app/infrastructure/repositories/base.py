from dataclasses import fields
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class SqlRepository(Generic[T]):
    """Repository SQLAlchemy générique : mappe modèles ORM <-> entités du domaine."""

    model: Any
    entity: type[T]

    def __init__(self, session: Session) -> None:
        self.s = session

    # --- mapping ---
    def _to_entity(self, obj) -> T | None:
        if obj is None:
            return None
        return self.entity(**{f.name: getattr(obj, f.name) for f in fields(self.entity)})  # type: ignore[arg-type]

    def _many(self, objs) -> list[T]:
        return [self._to_entity(o) for o in objs]  # type: ignore[misc]

    # --- CRUD ---
    def get(self, id: int) -> T | None:
        return self._to_entity(self.s.get(self.model, id))

    def add(self, entity: T) -> T:
        data = {f.name: getattr(entity, f.name) for f in fields(entity) if getattr(entity, f.name) is not None}  # type: ignore[arg-type]
        obj = self.model(**data)
        self.s.add(obj)
        self.s.flush()
        self.s.refresh(obj)
        return self._to_entity(obj)  # type: ignore[return-value]

    def update(self, entity: T) -> T:
        obj = self.s.get(self.model, entity.id)  # type: ignore[attr-defined]
        for f in fields(entity):  # type: ignore[arg-type]
            if f.name not in ("id", "created_at"):
                setattr(obj, f.name, getattr(entity, f.name))
        self.s.flush()
        return entity

    def delete(self, id: int) -> None:
        obj = self.s.get(self.model, id)
        if obj is not None:
            self.s.delete(obj)
            self.s.flush()

    def _first(self, stmt) -> T | None:
        return self._to_entity(self.s.execute(stmt).scalars().first())

    def _all(self, stmt) -> list[T]:
        return self._many(self.s.execute(stmt).scalars().all())
