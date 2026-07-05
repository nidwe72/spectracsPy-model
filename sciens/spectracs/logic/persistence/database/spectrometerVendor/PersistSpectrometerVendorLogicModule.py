from typing import Dict

from sciens.spectracs.logic.persistence.database.spectrometerVendor.PersistenceParametersGetSpectrometerVendors import \
    PersistenceParametersGetSpectrometerVendors
from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerVendor import SpectrometerVendor


class PersistSpectrometerVendorLogicModule:

    def saveSpectrometerVendor(self, spectrometerVendor:SpectrometerVendor):
        session = server_session_factory()
        session.add(spectrometerVendor)
        session.commit()

    def getSpectrometerVendors(self,
                               persistenceParametersGetSpectrometerVendors: PersistenceParametersGetSpectrometerVendors) -> \
    Dict[int,SpectrometerVendor]:
        ids = persistenceParametersGetSpectrometerVendors.getIds()
        session = server_session_factory()
        resultList = session.query(SpectrometerVendor).all()

        result:Dict[int,SpectrometerVendor] = {}
        for spectrometerVendor in resultList:
            result[spectrometerVendor.id]=spectrometerVendor

        return result
