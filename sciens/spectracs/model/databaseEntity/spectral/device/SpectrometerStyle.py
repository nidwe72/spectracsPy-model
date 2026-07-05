from sqlalchemy import Column
from sqlalchemy import String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity

class SpectrometerStyle(ServerDbBaseEntity, DbBaseEntityMixin):
    styleId = Column(String)
    styleName = Column(String)
    description = Column(String)

