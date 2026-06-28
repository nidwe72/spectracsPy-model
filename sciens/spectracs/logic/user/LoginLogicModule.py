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
            return {"ok": False, "userId": None, "username": None, "roles": [], "message": "invalid credentials"}

        roles = persist.getRoleNamesForUser(appUser)
        return {"ok": True, "userId": appUser.id, "username": appUser.username, "roles": roles, "message": None}
