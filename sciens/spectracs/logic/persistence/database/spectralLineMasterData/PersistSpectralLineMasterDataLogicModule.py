from typing import Dict

from sqlalchemy.orm import class_mapper
from sqlalchemy import inspect

from sciens.spectracs.logic.model.util.databaseEntity.SqlUtil import SqlUtil
from sciens.spectracs.logic.persistence.database.spectralLineMasterData.PersistenceParametersGetSpectralLineMasterDatas import \
    PersistenceParametersGetSpectralLineMasterDatas
# SpectralLineMasterData now lives on the SERVER DB (moved with SpectralLine so the ORM relationship
# resolves in one registry — SPEC_connection_and_calibration_ux.md §9). SqlUtil.executeSelect is hardwired
# to the APP session, so the read below runs SqlUtil's (session-agnostic) select on the SERVER session.
from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLineMasterData import SpectralLineMasterData


class PersistSpectralLineMasterDataLogicModule:

    def saveSpectralLineMasterData(self, spectralLineMasterData: SpectralLineMasterData):
        session = server_session_factory()
        session.add(spectralLineMasterData)
        session.commit()


    def getSpectralLineMasterDatas(self,
                                   moduleParameters: PersistenceParametersGetSpectralLineMasterDatas) -> \
            Dict[int, SpectralLineMasterData]:

        if moduleParameters is None:
            moduleParameters = PersistenceParametersGetSpectralLineMasterDatas()

        baseEntity = moduleParameters.getBaseEntity()
        selectStatement = SqlUtil.createSelect(baseEntity)

        # Execute on the SERVER session (mirror of SqlUtil.executeSelect, which uses the app session).
        session = server_session_factory()
        primaryKeys = [key.name for key in inspect(baseEntity.__class__).primary_key]
        primaryKey = next(iter(primaryKeys), None)
        resultList = session.execute(selectStatement).all()
        resultList = [next(iter(entry._asdict().values()), None) for entry in resultList]
        result = {getattr(entry, primaryKey): entry for entry in resultList}

        return result

    def getChangedAttributes(self, entity):
        result = []
        inspr = inspect(entity)
        attrs = class_mapper(entity.__class__).column_attrs  # exclude relationships
        for attr in attrs:
            hist = getattr(inspr.attrs, attr.key).history
            if hist.has_changes():
                result.append(attr)
        return result
