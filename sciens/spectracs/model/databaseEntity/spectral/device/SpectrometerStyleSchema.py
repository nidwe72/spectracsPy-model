from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerStyle import SpectrometerStyle


class SpectrometerStyleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpectrometerStyle
        include_relationships = True
        load_instance = True

