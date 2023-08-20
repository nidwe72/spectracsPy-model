from sqlalchemy import Column, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensor import SpectrometerSensor
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerStyle import SpectrometerStyle
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerVendor import SpectrometerVendor


class Spectrometer(DbBaseEntity, DbBaseEntityMixin):

    modelName=Column(String)

    spectrometerSensorId = Column(String, ForeignKey("spectrometer_sensor.id"))

    SpectrometerSensor()
    spectrometerSensor = relationship("SpectrometerSensor")

    spectrometerVendorId = Column(String, ForeignKey("spectrometer_vendor.id"))
    SpectrometerVendor()
    spectrometerVendor = relationship("SpectrometerVendor")

    spectrometerStyleId = Column(String, ForeignKey("spectrometer_style.id"))
    SpectrometerStyle()
    spectrometerStyle = relationship("SpectrometerStyle")



