from sciens.spectracs.logic.instrument.InstrumentLogicModule import InstrumentLogicModule
from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.logic.user.PasswordUtil import PasswordUtil
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser
from sciens.spectracs.model.databaseEntity.application.user.AppUserToAppUserRole import AppUserToAppUserRole
from sciens.spectracs.model.databaseEntity.application.user.UserRoleType import UserRoleType


class RegisterUserLogicModule:
    """End-user self-registration (SPEC_connection_and_calibration_ux.md §4.2).

    The serial must already resolve to a master-authored instrument (else the factory-calibration message).
    Username must be unique; the serial must not already be registered (1:1). Always role END_USER.
    Returns a plain dict; on success it carries the resolved bundle so the client can go straight to the
    session (auto-login).
    """

    PASSWORD_MIN_LENGTH = 8

    def registerEndUser(self, username: str, password: str, email: str,
                        firstName: str, lastName: str, serial: str) -> dict:
        persist = PersistUserLogicModule()

        if not username or not password:
            return {"ok": False, "message": "username and password are required"}
        if len(password) < self.PASSWORD_MIN_LENGTH:
            return {"ok": False, "message": "password must be at least %d characters" % self.PASSWORD_MIN_LENGTH}
        if not email:
            return {"ok": False, "message": "email is required"}

        bundle = InstrumentLogicModule().resolveBundle(serial)
        if not bundle.get("ok"):
            return {"ok": False, "message": bundle.get("message")}

        if persist.findUserByUsername(username) is not None:
            return {"ok": False, "message": "username already taken"}
        if persist.findUserByRegisteredSerial(serial) is not None:
            return {"ok": False, "message": "this spectrometer is already registered to another user"}

        appUser = AppUser()
        appUser.username = username
        appUser.passwordHash = PasswordUtil().hash(password)
        appUser.displayName = ((firstName or "") + " " + (lastName or "")).strip() or username
        appUser.enabled = True
        appUser.email = email
        appUser.firstName = firstName
        appUser.lastName = lastName
        appUser.registeredSerial = serial
        persist.saveUser(appUser)

        role = persist.findRoleByName(UserRoleType.END_USER.value)
        link = AppUserToAppUserRole()
        link.app_user_id = appUser.id
        link.app_user_role_id = role.id
        persist.saveUserToRole(link)

        return {"ok": True, "userId": appUser.id, "username": username,
                "roles": [UserRoleType.END_USER.value], "bundle": bundle, "message": None}
