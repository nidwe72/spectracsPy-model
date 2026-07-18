"""Boot-time database initialisation — the guarded-init policy (SPEC_schema_migrations.md §3.3, policy c).

Run ONCE at each process's startup, before any session use: the app process inits the app DB, the server
process inits the server DB. Per DB:

  1. no tables yet          -> create_all (fast, builds head) + stamp head   (tests + fresh installs land here)
  2. tables + alembic_version -> upgrade head                                 (the real-world evolve case)
  3. tables, no alembic_version -> stamp baseline + upgrade head              (adopt a pre-Alembic DB)

Keeping create_all as the fresh-schema builder is deliberate: the test-suite relies on it, and it never touches
alembic_version, so tests neither slow down nor need the Alembic env. Alembic only ever *evolves* an existing DB.
A DRIFTED pre-Alembic dev DB (missing a baseline column) must be deleted + reseeded, not adopted (case 3 assumes
the baseline schema is present)."""
import os

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, engine as appEngine
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity, serverEngine
import sciens.spectracs.model.databaseEntity.AllEntities  # noqa: F401  -- populate both metadatas

# -model repo root (…/spectracsPy-model), four levels up from this file's package dir.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _config(dbName: str) -> Config:
    return Config(os.path.join(_ROOT, "alembic", dbName, "alembic.ini"))


def _init(engine, metadata, dbName: str) -> None:
    cfg = _config(dbName)
    tableNames = inspect(engine).get_table_names()
    userTables = [t for t in tableNames if t != "alembic_version"]

    if not userTables:                                   # 1) fresh
        metadata.create_all(engine)
        command.stamp(cfg, "head")
    elif "alembic_version" in tableNames:                # 2) evolve
        command.upgrade(cfg, "head")
    else:                                                # 3) adopt a pre-Alembic DB
        baseline = ScriptDirectory.from_config(cfg).get_bases()[0]
        command.stamp(cfg, baseline)
        command.upgrade(cfg, "head")


def initAppDatabase() -> None:
    _init(appEngine, DbBaseEntity.metadata, "app")


def initServerDatabase() -> None:
    _init(serverEngine, ServerDbBaseEntity.metadata, "server")
