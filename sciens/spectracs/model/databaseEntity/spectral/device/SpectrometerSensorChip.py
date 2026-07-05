from sqlalchemy import Column
from sqlalchemy import String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity

class SpectrometerSensorChip(ServerDbBaseEntity, DbBaseEntityMixin):

    vendorName = Column(String)
    productName = Column(String)


