from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from sciens.spectracs.model.databaseEntity.spectral.device.Spectrometer import Spectrometer
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorSchema import SpectrometerSensorSchema
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerStyleSchema import SpectrometerStyleSchema
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerVendorSchema import SpectrometerVendorSchema


class SpectrometerSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = Spectrometer
        include_relationships = True
        load_instance = True

    spectrometerSensor = Nested(SpectrometerSensorSchema, many=False)
    spectrometerVendor = Nested(SpectrometerVendorSchema, many=False)
    spectrometerStyle = Nested(SpectrometerStyleSchema, many=False)
