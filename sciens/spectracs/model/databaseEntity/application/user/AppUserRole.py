from sqlalchemy import Column, String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class AppUserRole(ServerDbBaseEntity, DbBaseEntityMixin):

    name = Column(String, unique=True)
