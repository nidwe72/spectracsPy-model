from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensor import SpectrometerSensor


class SpectrometerSensorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpectrometerSensor
        include_relationships = True
        load_instance = True

