from sqlalchemy import Column, String, Boolean

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class AppUser(ServerDbBaseEntity, DbBaseEntityMixin):

    username = Column(String, unique=True)
    passwordHash = Column(String)
    displayName = Column(String)
    enabled = Column(Boolean, default=True)
