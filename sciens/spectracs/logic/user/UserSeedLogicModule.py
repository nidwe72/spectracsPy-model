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

    # Demo serial-keyed instrument (SPEC_connection_and_calibration_ux.md §9): binds the virtual device +
    # pumpkin plugin under one serial, and the pumpkin demo user registers it. XXXX-XXXX format.
    DEMO_SERIAL = "TEST-0001"

    def seed(self):
        self.__seedRoles()
        self.__seedUsers()
        self.__seedPumpkinBinding()  # plugin + bound demo user (after roles/users exist)
        self.__seedInstrument()      # serial -> SpectrometerSetup{virtual device, calibration, pumpkin plugin}

    def __applyIdentity(self, appUser, username):
        # New identity fields (SPEC_connection_and_calibration_ux.md §3.1-5). Dev placeholders.
        appUser.email = username + "@example.com"
        appUser.firstName = username
        appUser.lastName = "User"

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
            self.__applyIdentity(appUser, username)
            persist.saveUser(appUser)

            role = persist.findRoleByName(roleType.value)
            link = AppUserToAppUserRole()
            link.app_user_id = appUser.id
            link.app_user_role_id = role.id
            persist.saveUserToRole(link)

    def __seedPumpkinBinding(self):
        # Create the pumpkin demo user (identity + END_USER role). Its instrument binding (plugin + device)
        # is NOT on the user any more — it flows from registeredSerial, set in __seedInstrument.
        persist = PersistUserLogicModule()

        username, password, roleType = self.PUMPKIN_TEST_USER
        if persist.findUserByUsername(username) is not None:
            return

        appUser = AppUser()
        appUser.username = username
        appUser.passwordHash = PasswordUtil().hash(password)
        appUser.displayName = username
        appUser.enabled = True
        self.__applyIdentity(appUser, username)
        persist.saveUser(appUser)

        role = persist.findRoleByName(roleType.value)
        link = AppUserToAppUserRole()
        link.app_user_id = appUser.id
        link.app_user_role_id = role.id
        persist.saveUserToRole(link)

    def __seedInstrument(self):
        # Establish ONE serial-keyed instrument (SPEC_connection_and_calibration_ux.md §9): the virtual
        # device + an (empty) calibration + the pumpkin plugin, bound under DEMO_SERIAL, and register the
        # pumpkin demo user against it. Idempotent on the serial. This gives resolveInstrumentBySerial (A3)
        # real data and exercises the new SpectrometerSetup FKs at boot.
        from sciens.spectracs.logic.model.util.SpectrometerUtil import SpectrometerUtil
        from sciens.spectracs.logic.persistence.database.spectrometerSetup.PersistSpectrometerSetupLogicModule import \
            PersistSpectrometerSetupLogicModule

        dbPlugin = PersistPluginLogicModule().getOrCreate(
            self.PUMPKIN_PLUGIN["title"], self.PUMPKIN_PLUGIN["codeRef"], self.PUMPKIN_PLUGIN["version"])

        spectrometers = SpectrometerUtil().getSpectrometers()  # get-or-creates the catalog server-side
        virtual = next((s for s in spectrometers.values()
                        if s.spectrometerSensor.codeName == self.VIRTUAL_DEVICE_CODE_NAME), None)
        if virtual is None:
            return

        PersistSpectrometerSetupLogicModule().getOrCreateInstrument(self.DEMO_SERIAL, virtual.id, dbPlugin.id)

        # Register the pumpkin demo user against the serial (additive to the legacy pluginId binding).
        persist = PersistUserLogicModule()
        user = persist.findUserByUsername(self.PUMPKIN_TEST_USER[0])
        if user is not None and user.registeredSerial is None:
            user.registeredSerial = self.DEMO_SERIAL
            persist.updateUser(user)
