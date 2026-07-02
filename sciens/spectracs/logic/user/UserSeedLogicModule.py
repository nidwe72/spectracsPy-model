from sciens.spectracs.logic.persistence.database.plugin.PersistPluginLogicModule import PersistPluginLogicModule
from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.logic.user.PasswordUtil import PasswordUtil
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser
from sciens.spectracs.model.databaseEntity.application.user.AppUserRole import AppUserRole
from sciens.spectracs.model.databaseEntity.application.user.AppUserToAppUserRole import AppUserToAppUserRole
from sciens.spectracs.model.databaseEntity.application.user.UserRoleType import UserRoleType
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorCodeName import SpectrometerSensorCodeName


class UserSeedLogicModule:
    """Idempotent startup seeding: the two roles, the DEVELOPMENT-ONLY users, and the pumpkin demo
    plugin + a demo end-user bound to it (SPEC_pumpkin_integration.md B.1a).

    WARNING: these are plaintext dev credentials. Do NOT ship them to a real deployment.
    """

    SEED_USERS = [
        ("endUser", "endUser", UserRoleType.END_USER),
        ("masterUser", "masterUser", UserRoleType.MASTER_USER),
    ]

    # The pumpkin demo plugin the master "authors" + the end-user configured to run it.
    PUMPKIN_PLUGIN = {
        "title": "Pumpkin-seed-oil colour QM",
        "codeRef": "sciens.spectracs.logic.spectral.plugin.pumpkin.PumpkinOilPlugin.PumpkinOilPlugin",
        "version": "1.0",
    }
    PUMPKIN_TEST_USER = ("pumpkinTestUser", "pumpkinTestUser", UserRoleType.END_USER)
    VIRTUAL_DEVICE_CODE_NAME = SpectrometerSensorCodeName.VIRTUAX.value  # "Virtuax"

    def seed(self):
        self.__seedRoles()
        self.__seedUsers()
        self.__seedPumpkinBinding()  # plugin + bound demo user (after roles/users exist)

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

    def __seedPumpkinBinding(self):
        persist = PersistUserLogicModule()
        # 1) the plugin row (get-or-create, idempotent on codeRef) — before the bound user needs its id.
        dbPlugin = PersistPluginLogicModule().getOrCreate(
            self.PUMPKIN_PLUGIN["title"], self.PUMPKIN_PLUGIN["codeRef"], self.PUMPKIN_PLUGIN["version"])

        username, password, roleType = self.PUMPKIN_TEST_USER
        existing = persist.findUserByUsername(username)
        if existing is not None:
            # Upgrade an already-seeded user whose binding is missing (robust across partial prior runs).
            if existing.pluginId is None or existing.spectrometerDevice is None:
                existing.pluginId = dbPlugin.id
                existing.spectrometerDevice = self.VIRTUAL_DEVICE_CODE_NAME
                persist.updateUser(existing)
            return

        appUser = AppUser()
        appUser.username = username
        appUser.passwordHash = PasswordUtil().hash(password)
        appUser.displayName = username
        appUser.enabled = True
        appUser.pluginId = dbPlugin.id
        appUser.spectrometerDevice = self.VIRTUAL_DEVICE_CODE_NAME
        persist.saveUser(appUser)

        role = persist.findRoleByName(roleType.value)
        link = AppUserToAppUserRole()
        link.app_user_id = appUser.id
        link.app_user_role_id = role.id
        persist.saveUserToRole(link)
