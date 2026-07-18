"""Alembic environment for the SERVER database (spectracsPyServer.db / ServerDbBaseEntity).
SPEC_schema_migrations.md §3.2 — one env per DB, both trees in -model. Batch mode on (SQLite-safe ALTER)."""
from alembic import context

from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity, serverEngine
import sciens.spectracs.model.databaseEntity.AllEntities  # noqa: F401  -- populate the metadata

target_metadata = ServerDbBaseEntity.metadata


def run_migrations_offline():
    context.configure(
        url=str(serverEngine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with serverEngine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
