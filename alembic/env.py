from logging.config import fileConfig
from alembic import context
from sqlmodel import SQLModel

# Order matters: import the engine FIRST so create_db_and_tables() runs and
# SQLModel.metadata is fully populated before Alembic reads it.
from friday.core.database import engine as friday_engine
from friday.llm.models.db_models import (  # noqa: F401
    LLMProvider,
    APIKey,
    ModelEntry,
    ActiveSession,
)

# ── Alembic config ─────────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Override sqlalchemy.url with the project's actual engine URL so alembic.ini
# doesn't need a hard-coded path.
config.set_main_option("sqlalchemy.url", str(friday_engine.url))


# ── Migration runners ──────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the live DB engine."""
    connectable = friday_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # required for SQLite ALTER TABLE support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
