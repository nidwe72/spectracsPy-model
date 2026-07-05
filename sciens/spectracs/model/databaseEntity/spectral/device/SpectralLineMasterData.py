from sqlalchemy import Column, Float
from sqlalchemy import String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class SpectralLineMasterData(ServerDbBaseEntity, DbBaseEntityMixin):
    name = Column(String)
    colorName = Column(String)
    mainColorName = Column(String)
    nanometer = Column(Float)


    intensity:int=0
    description:str=''
    light='CFL'




