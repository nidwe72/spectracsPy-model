from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.Spectrometer import Spectrometer


class SpectrometerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Spectrometer
        include_relationships = True
        load_instance = True
