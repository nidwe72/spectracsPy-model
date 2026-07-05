from typing import Dict

from sciens.spectracs.logic.persistence.database.spectrometerProfile.PersistenceParametersGetSpectrometerProfiles import \
    PersistenceParametersGetSpectrometerProfiles
from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerProfile import SpectrometerProfile


class PersistSpectrometerProfileLogicModule:

    def saveSpectrometerProfile(self, spectrometerProfile: SpectrometerProfile):
        session = server_session_factory()
        session.add(spectrometerProfile)
        session.commit()

    def getSpectrometerProfile(self,
                               persistenceParametersGetSpectrometerProfile: PersistenceParametersGetSpectrometerProfiles) -> \
    Dict[int, SpectrometerProfile]:

        ids = persistenceParametersGetSpectrometerProfile.getIds()
        session = server_session_factory()
        resultList = session.query(SpectrometerProfile).all()
        result: Dict[int, SpectrometerProfile] = {}
        for spectrometer in resultList:
            result[spectrometer.id] = spectrometer
        return result
