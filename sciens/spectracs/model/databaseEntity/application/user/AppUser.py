from sqlalchemy import Column, String, Boolean

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class AppUser(ServerDbBaseEntity, DbBaseEntityMixin):

    username = Column(String, unique=True)
    passwordHash = Column(String)
    displayName = Column(String)
    enabled = Column(Boolean, default=True)

    # --- identity (SPEC_connection_and_calibration_ux.md §3.1-5) ---
    email = Column(String)       # mandatory at self-registration (support/feedback mailing)
    firstName = Column(String)
    lastName = Column(String)
    # serial (XXXX-XXXX) of the SpectrometerSetup this end-user registered — the binding key. The instrument
    # bundle (device + calibration + plugin) resolves through this serial via SpectrometerSetup, NOT through
    # a per-user plugin binding. One user <-> one serial for now. (SPEC_connection_and_calibration_ux.md §3.)
    registeredSerial = Column(String)
