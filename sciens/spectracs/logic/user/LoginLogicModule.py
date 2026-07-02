from typing import Dict

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
            return {"ok": False, "userId": None, "username": None, "roles": [],
                    "pluginId": None, "pluginCodeRef": None, "spectrometerDevice": None,
                    "message": "invalid credentials"}

        roles = persist.getRoleNamesForUser(appUser)
        # The config binding travels with login so the client can "download" the plugin + device (concept
        # §9.5). Resolve the plugin's codeRef here (client can't query the server DB) so it can import it.
        pluginCodeRef = appUser.plugin.codeRef if appUser.plugin is not None else None
        return {"ok": True, "userId": appUser.id, "username": appUser.username, "roles": roles,
                "pluginId": appUser.pluginId, "pluginCodeRef": pluginCodeRef,
                "spectrometerDevice": appUser.spectrometerDevice, "message": None}
