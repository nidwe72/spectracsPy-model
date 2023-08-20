from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorChip import SpectrometerSensorChip


class SpectrometerSensorChipSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpectrometerSensorChip
        include_relationships = True
        load_instance = True
        transient = True

