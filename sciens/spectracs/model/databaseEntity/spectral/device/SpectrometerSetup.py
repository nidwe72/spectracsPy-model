from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity
# Import FK targets before mapper configuration so relationship() strings resolve.
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerProfile import SpectrometerProfile
from sciens.spectracs.model.databaseEntity.application.plugin.DbPlugin import DbPlugin


class SpectrometerSetup(ServerDbBaseEntity, DbBaseEntityMixin):
    # Parent deployment/assignment object — SPEC_connection_and_calibration_ux.md §3.1-7.
    # Binds a serial-keyed SpectrometerProfile (device + calibration = factory hardware truth) to the
    # plugin the instrument runs. SERVER-DB so both FKs are real (SpectrometerProfile + DbPlugin now live
    # on the server DB too). The serial itself lives on SpectrometerProfile; resolve-by-serial walks
    # SpectrometerProfile.serial -> its SpectrometerSetup -> plugin. Tablename derives to "spectrometer_setup".

    spectrometerProfileId = Column(String, ForeignKey("spectrometer_profile.id"))
    spectrometerProfile = relationship("SpectrometerProfile")

    pluginId = Column(String, ForeignKey("db_plugin.id"))
    plugin = relationship("DbPlugin")
