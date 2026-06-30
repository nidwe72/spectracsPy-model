from typing import Dict, List

from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.logic.user.PasswordUtil import PasswordUtil
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser
from sciens.spectracs.model.databaseEntity.application.user.UserRoleType import UserRoleType


class UserAdminLogicModule:
    """Server-side user administration (master-user CRUD). Returns plain dicts only — never an
    AppUser entity, never the password hash (mirrors the LoginLogicModule dict convention).

    A password only ever travels client -> server here; the hash never travels back.
    """

    PASSWORD_MIN_LENGTH = 8

    def listUsers(self) -> List[Dict]:
        persist = PersistUserLogicModule()
        return [self.__toDto(appUser, persist) for appUser in persist.listAllUsers()]

    def createUser(self, username, password, displayName, enabled, roleName) -> Dict:
        persist = PersistUserLogicModule()

        username = (username or "").strip()
        if username == "":
            return self.__error("username must not be empty")
        if password is None or len(password) < self.PASSWORD_MIN_LENGTH:
            return self.__error("password must be at least %d characters" % self.PASSWORD_MIN_LENGTH)
        if persist.findUserByUsername(username) is not None:
            return self.__error("username already exists")

        appUser = AppUser()
        appUser.username = username
        appUser.passwordHash = PasswordUtil().hash(password)
        appUser.displayName = displayName
        appUser.enabled = bool(enabled)
        persist.saveUser(appUser)
        persist.replaceUserRoles(appUser, [roleName])

        return {"ok": True, "userId": appUser.id, "message": None}

    def updateUser(self, userId, displayName, enabled, roleName, newPassword) -> Dict:
        persist = PersistUserLogicModule()

        appUser = persist.findUserById(userId)
        if appUser is None:
            return self.__error("user not found")

        enabled = bool(enabled)

        # Last-master-user guard: refuse a change that would disable or demote the only
        # remaining enabled master, so admin access can never be locked out.
        if self.__isLastEnabledMaster(appUser, persist):
            losesMaster = roleName != UserRoleType.MASTER_USER.value
            if (not enabled) or losesMaster:
                return self.__error("cannot disable or demote the last master user")

        if newPassword is not None and newPassword != "":
            if len(newPassword) < self.PASSWORD_MIN_LENGTH:
                return self.__error("password must be at least %d characters" % self.PASSWORD_MIN_LENGTH)
            appUser.passwordHash = PasswordUtil().hash(newPassword)

        # Username is immutable (identity / future serial) — intentionally not updated here.
        appUser.displayName = displayName
        appUser.enabled = enabled
        persist.updateUser(appUser)
        persist.replaceUserRoles(appUser, [roleName])

        return {"ok": True, "userId": appUser.id, "message": None}

    def deleteUser(self, userId) -> Dict:
        persist = PersistUserLogicModule()

        appUser = persist.findUserById(userId)
        if appUser is None:
            return self.__error("user not found")

        if self.__isLastEnabledMaster(appUser, persist):
            return self.__error("cannot delete the last master user")

        persist.deleteUser(userId)
        return {"ok": True, "userId": userId, "message": None}

    def __isLastEnabledMaster(self, appUser: AppUser, persist: PersistUserLogicModule) -> bool:
        roles = persist.getRoleNamesForUser(appUser)
        if (not appUser.enabled) or UserRoleType.MASTER_USER.value not in roles:
            return False
        return persist.countUsersWithRole(UserRoleType.MASTER_USER.value) <= 1

    def __toDto(self, appUser: AppUser, persist: PersistUserLogicModule) -> Dict:
        roles = persist.getRoleNamesForUser(appUser)
        return {"userId": appUser.id, "username": appUser.username,
                "displayName": appUser.displayName, "enabled": appUser.enabled, "roles": roles}

    def __error(self, message: str) -> Dict:
        return {"ok": False, "userId": None, "message": message}
