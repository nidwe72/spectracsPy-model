from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.logic.user.PasswordUtil import PasswordUtil
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser
from sciens.spectracs.model.databaseEntity.application.user.AppUserRole import AppUserRole
from sciens.spectracs.model.databaseEntity.application.user.AppUserToAppUserRole import AppUserToAppUserRole
from sciens.spectracs.model.databaseEntity.application.user.UserRoleType import UserRoleType


class UserSeedLogicModule:
    """Idempotent startup seeding: the two roles + two DEVELOPMENT-ONLY users.

    WARNING: these are plaintext dev credentials. Do NOT ship them to a real deployment.
    """

    SEED_USERS = [
        ("endUser", "endUser", UserRoleType.END_USER),
        ("masterUser", "masterUser", UserRoleType.MASTER_USER),
    ]

    def seed(self):
        self.__seedRoles()
        self.__seedUsers()

    def __seedRoles(self):
        persist = PersistUserLogicModule()
        for roleType in UserRoleType:
            if persist.findRoleByName(roleType.value) is None:
                role = AppUserRole()
                role.name = roleType.value
                persist.saveRole(role)

    def __seedUsers(self):
        persist = PersistUserLogicModule()
        passwordUtil = PasswordUtil()
        for username, password, roleType in self.SEED_USERS:
            if persist.findUserByUsername(username) is not None:
                continue

            appUser = AppUser()
            appUser.username = username
            appUser.passwordHash = passwordUtil.hash(password)
            appUser.displayName = username
            appUser.enabled = True
            persist.saveUser(appUser)

            role = persist.findRoleByName(roleType.value)
            link = AppUserToAppUserRole()
            link.app_user_id = appUser.id
            link.app_user_role_id = role.id
            persist.saveUserToRole(link)
