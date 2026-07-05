from sqlalchemy import ForeignKey, Column, Boolean, String
from sqlalchemy.orm import Mapped

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin

class ApplicationConfigToSpectrometerProfile(DbBaseEntity,DbBaseEntityMixin):

    isDefault = Column('isDefault', Boolean, default=False)

    application_config_id: Mapped[str] = Column(ForeignKey("application_config.id"), primary_key=True)

    # SpectrometerProfile now lives on the SERVER DB (SPEC_connection_and_calibration_ux.md §3 / A2), so
    # a cross-database ForeignKey/relationship is impossible. This is a SOFT id reference; the profile is
    # looked up over the server DB by id. The whole ApplicationConfig active-profile mechanism is retired
    # in A4 (active instrument = the logged-in user's registeredSerial) — this decouple is that first step.
    spectrometer_profile_id: Mapped[str] = Column(String, primary_key=True)


