
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin

# import pdb; pdb.set_trace()

class SpectrometerCalibrationProfile(DbBaseEntity, DbBaseEntityMixin):

    regionOfInterestX1 = Column(Integer)
    regionOfInterestY1 = Column(Integer)

    regionOfInterestX2 = Column(Integer)
    regionOfInterestY2 = Column(Integer)

    interpolationCoefficientA = Column(Float)
    interpolationCoefficientB = Column(Float)
    interpolationCoefficientC = Column(Float)
    interpolationCoefficientD = Column(Float)

    spectralLines = relationship("SpectralLine", back_populates="spectrometerCalibrationProfile")

    def getSpectralLines(self):
        return self.spectralLines

    def setSpectralLines(self,spectralLines):
        self.spectralLines=spectralLines






