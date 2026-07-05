from typing import ClassVar

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity

try:
    from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLine import SpectralLine
except ImportError:
    pass




# import pdb; pdb.set_trace()

class SpectrometerCalibrationProfile(ServerDbBaseEntity, DbBaseEntityMixin):

    regionOfInterestX1 = Column(Integer)
    regionOfInterestY1 = Column(Integer)

    regionOfInterestX2 = Column(Integer)
    regionOfInterestY2 = Column(Integer)

    interpolationCoefficientA = Column(Float)
    interpolationCoefficientB = Column(Float)
    interpolationCoefficientC = Column(Float)
    interpolationCoefficientD = Column(Float)

    # The raw CFL capture used to calibrate, stored via the common Spectrum serialization
    # (Spectrum.toJson() = {str(pixelIndex): intensity}); provenance that a sane CFL spectrum was used.
    calibrationSpectrumJson = Column(Text)

    spectralLines = relationship("SpectralLine", back_populates="spectrometerCalibrationProfile",
                                 cascade="all, delete-orphan")

    # Transient (NOT mapped): the in-memory Spectrum object, attached during detection and rebuilt from
    # calibrationSpectrumJson on load. Harvested by the setup editor's Save into calibrationSpectrumJson.
    calibrationSpectrum: ClassVar[object] = None

    def getSpectralLines(self):
        return self.spectralLines

    def setSpectralLines(self,spectralLines):
        self.spectralLines=spectralLines






