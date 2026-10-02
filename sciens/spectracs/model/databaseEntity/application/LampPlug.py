from sqlalchemy import Column, String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin


class LampPlug(DbBaseEntity, DbBaseEntityMixin):
    # The lamp plug this machine found last time, and its password (SPEC_lamp_switch.md §6, D9). APP DB, not the
    # server: the plug belongs to this desk's network. The app keeps ONE row — the plug it uses.
    #
    # ⚠ The password is stored in PLAIN TEXT: the plug's API only accepts digest auth computed from the clear
    # password, so a hash would be useless. Acceptable for a plug password on a lab machine (§6).

    driverName = Column(String)
    host = Column(String)
    mac = Column(String, unique=True)
    model = Column(String)
    deviceId = Column(String)
    password = Column(String, nullable=True)
