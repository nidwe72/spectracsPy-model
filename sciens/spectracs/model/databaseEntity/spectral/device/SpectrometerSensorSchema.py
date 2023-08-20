from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensor import SpectrometerSensor
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorChip import SpectrometerSensorChip
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorChipSchema import \
    SpectrometerSensorChipSchema


class SpectrometerSensorSchema(SQLAlchemyAutoSchema):

    spectrometerSensorChip = Nested(SpectrometerSensorChipSchema, many=False)

    class Meta:
        model = SpectrometerSensor
        include_relationships = True
        load_instance = True
        transient = True
