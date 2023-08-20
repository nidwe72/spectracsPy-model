from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerVendor import SpectrometerVendor


class SpectrometerVendorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpectrometerVendor
        include_relationships = True
        load_instance = True

