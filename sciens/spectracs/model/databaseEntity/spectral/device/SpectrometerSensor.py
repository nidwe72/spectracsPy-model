from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy import String
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorChip import SpectrometerSensorChip


class SpectrometerSensor(DbBaseEntity, DbBaseEntityMixin):

    vendorId = Column(String)
    vendorName = Column(String)
    sellerName = Column(String)
    modelId = Column(String)
    description = Column(String)
    codeName=Column(String)
    isVirtual=Column(Boolean)

    spectrometerSensorChipId = Column(String, ForeignKey("spectrometer_sensor_chip.id"))
    SpectrometerSensorChip()
    spectrometerSensorChip = relationship("SpectrometerSensorChip")



