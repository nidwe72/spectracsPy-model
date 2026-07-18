"""Alembic environment for the APP database (spectracsPy.db / DbBaseEntity).
SPEC_schema_migrations.md §3.2 — one env per DB, both trees in -model. Batch mode on (SQLite-safe ALTER)."""
from alembic import context

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, engine
import sciens.spectracs.model.databaseEntity.AllEntities  # noqa: F401  -- populate the metadata

target_metadata = DbBaseEntity.metadata


def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
