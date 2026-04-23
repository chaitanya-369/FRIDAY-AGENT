from sqlmodel import SQLModel, create_engine, Session
import friday.llm.models.db_models  # noqa: F401

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


_seeded = False


def create_db_and_tables():
    """Create all tables and seed providers/keys/models from .env (idempotent)."""
    global _seeded
    SQLModel.metadata.create_all(engine)
    if not _seeded:
        from friday.llm.seeder import seed_providers_and_keys

        seed_providers_and_keys()
        _seeded = True


def get_session():
    with Session(engine) as session:
        yield session
