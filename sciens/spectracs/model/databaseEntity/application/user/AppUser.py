from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity
# Import registers DbPlugin BEFORE the AppUser mapper configures, so relationship("DbPlugin") resolves.
from sciens.spectracs.model.databaseEntity.application.plugin.DbPlugin import DbPlugin


class AppUser(ServerDbBaseEntity, DbBaseEntityMixin):

    username = Column(String, unique=True)
    passwordHash = Column(String)
    displayName = Column(String)
    enabled = Column(Boolean, default=True)

    # --- config binding (SPEC_pumpkin_integration.md B.1a / D3 / D15) ---
    pluginId = Column(String, ForeignKey("db_plugin.id"))  # REAL FK — same server DB
    plugin = relationship("DbPlugin")
    spectrometerDevice = Column(String)  # stable device code-name (e.g. "Virtuax") — NOT a random profile id
