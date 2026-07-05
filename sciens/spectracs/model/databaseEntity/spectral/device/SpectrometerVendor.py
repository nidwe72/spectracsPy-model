from sqlalchemy import Column
from sqlalchemy import String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity

class SpectrometerVendor(ServerDbBaseEntity, DbBaseEntityMixin):

    vendorName = Column(String)
    vendorId = Column(String)



