from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from sciens.base.Singleton import Singleton

# Reuse the same app-data location resolver as the app DB, but a SEPARATE database file.
# The user store is server-owned and must live apart from the app's spectracsPy.db.
from sciens.spectracs.model.databaseEntity.AppDataPathUtil import get_app_data_dir

serverDbFilepath = 'sqlite:///' + get_app_data_dir() + '/spectracsPyServer.db'
serverEngine = create_engine(serverDbFilepath)

_ServerSessionFactory = sessionmaker(bind=serverEngine, expire_on_commit=False)

# A declarative base with its OWN metadata, distinct from DbBase.DbBaseEntity. Because the two
# metadatas are separate, create_all() on each side only builds its own tables: the user tables
# exist only in spectracsPyServer.db, and the app's create_all never sees them.
ServerDbBaseEntity = declarative_base()


def server_session_factory() -> Session:
    ServerDbBaseEntity.metadata.create_all(serverEngine)
    return ServerSessionProvider().getSession()


class ServerSessionProvider(Singleton):
    session = None

    def getSession(self):
        if self.session is None:
            self.session = _ServerSessionFactory()
        return self.session
