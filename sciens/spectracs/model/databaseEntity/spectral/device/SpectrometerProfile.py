from sqlalchemy import Column, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.spectral.device.Spectrometer import Spectrometer
from sciens.spectracs.model.databaseEntity.spectral.device.calibration.SpectrometerCalibrationProfile import \
    SpectrometerCalibrationProfile


class SpectrometerProfile(DbBaseEntity, DbBaseEntityMixin):

    serial = Column(String)

    spectrometerId = Column(String, ForeignKey("spectrometer.id"))
    Spectrometer()
    spectrometer = relationship("Spectrometer")

    SpectrometerCalibrationProfile()
    spectrometerCalibrationProfileId = Column(String, ForeignKey("spectrometer_calibration_profile.id"))
    spectrometerCalibrationProfile = relationship("SpectrometerCalibrationProfile")

























