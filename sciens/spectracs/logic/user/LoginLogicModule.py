from typing import Dict

from sciens.spectracs.logic.instrument.InstrumentLogicModule import InstrumentLogicModule
from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.logic.user.PasswordUtil import PasswordUtil


class LoginLogicModule:
    """Server-side login. Returns a plain dict (Pyro-serializable as-is) — never the password hash,
    never an AppUser entity."""

    def login(self, username: str, password: str) -> Dict:
        persist = PersistUserLogicModule()
        appUser = persist.findUserByUsername(username)

        if appUser is None or not appUser.enabled or not PasswordUtil().verify(password, appUser.passwordHash):
            # Same generic message for unknown-user and wrong-password (don't leak account existence).
            return {"ok": False, "userId": None, "username": None, "roles": [], "registeredSerial": None,
                    "pluginCodeRef": None, "spectrometerDevice": None, "calibration": None,
                    "message": "invalid credentials"}

        roles = persist.getRoleNamesForUser(appUser)
        # The instrument bundle travels with login so the client can "download" its device + calibration +
        # plugin (SPEC_connection_and_calibration_ux.md §4.3). Resolved from the user's registered SERIAL
        # (not a per-user plugin binding any more) — client can't query the server DB, so resolve here.
        bundle = InstrumentLogicModule().resolveBundle(appUser.registeredSerial)
        ok = bool(bundle.get("ok"))
        return {"ok": True, "userId": appUser.id, "username": appUser.username, "roles": roles,
                "registeredSerial": appUser.registeredSerial,
                "pluginCodeRef": bundle.get("pluginCodeRef") if ok else None,
                "spectrometerDevice": bundle.get("deviceCodeName") if ok else None,
                "calibration": bundle.get("calibration") if ok else None,
                "message": None}
