from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_is_sqlite = settings.sqlalchemy_url.startswith("sqlite")
_kwargs = {"connect_args": {"check_same_thread": False}} if _is_sqlite else {"pool_recycle": 3600}
engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True, **_kwargs)

if _is_sqlite:  # active les clés étrangères en test
    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
