from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLineMasterData import SpectralLineMasterData


class SpectralLineMasterDataSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpectralLineMasterData
        include_relationships = True
        load_instance = True
        transient = True
