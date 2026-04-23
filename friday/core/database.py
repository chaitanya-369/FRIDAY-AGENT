"""
friday/core/database.py

SQLite engine and table creation for FRIDAY-AGENT.

IMPORTANT — import ordering is carefully designed to break circular references:
  1. `engine` is created FIRST so any circular import that needs it mid-cycle
     will find it available on the partially-initialised module.
  2. Submodule imports (to register SQLModel table metadata) come AFTER `engine`
     is defined, so the cycle resolves correctly.
  3. The seeder import stays inside create_db_and_tables() (lazy) to avoid
     pulling in the full LLM stack at module load time.
"""

from sqlmodel import SQLModel, create_engine, Session

# ── Engine MUST be defined before any submodule imports ──────────────────────
# Any module in the import cycle that does `from friday.core.database import engine`
# will find this attribute already set, even if database.py is still initialising.
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

# ── Register SQLModel table metadata (triggers schema imports) ────────────────
# These imports happen AFTER `engine` is bound, so the circular dependency
# (db_models/schema → database → engine) resolves cleanly.
import friday.llm.models.db_models  # noqa: E402, F401 — registers LLM tables; must be after engine
import friday.memory.schema  # noqa: E402, F401 — registers memory tables; must be after engine


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
