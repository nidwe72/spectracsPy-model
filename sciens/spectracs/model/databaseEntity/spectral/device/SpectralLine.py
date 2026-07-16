from typing import ClassVar

from sciens.spectracs.model.spectral.SpectralColor import SpectralColor
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer,String
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity
from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLineMasterData import SpectralLineMasterData

try:
    from sciens.spectracs.model.databaseEntity.spectral.device.calibration.SpectrometerCalibrationProfile import \
        SpectrometerCalibrationProfile
except ImportError:
    pass

class SpectralLine(ServerDbBaseEntity, DbBaseEntityMixin):

    pixelIndex=Column(Integer)

    spectrometerCalibrationProfile_id = Column(String, ForeignKey("spectrometer_calibration_profile.id"))
    spectrometerCalibrationProfile = relationship("SpectrometerCalibrationProfile", back_populates="spectralLines")

    spectralLineMasterDataId = Column(String, ForeignKey("spectral_line_master_data.id"))

    SpectralLineMasterData()
    spectralLineMasterData = relationship("SpectralLineMasterData")

    #transient stuff follows
    color:ClassVar[SpectralColor]=None

    __prominence:ClassVar[float]=None

    __intensity:ClassVar[float]=None

    @property
    def prominence(self):
        return self.__prominence

    @prominence.setter
    def prominence(self, prominence):
        self.__prominence=prominence

    @property
    def intensity(self):
        return self.__intensity

    @intensity.setter
    def intensity(self, intensity):
        self.__intensity=intensity




