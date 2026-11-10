from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

PK = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    """Base déclarative de tous les modèles SQLAlchemy."""


def pk() -> Mapped[int]:
    return mapped_column(PK, primary_key=True, autoincrement=True)


def created() -> Mapped[datetime]:
    return mapped_column(DateTime, server_default=func.now())
