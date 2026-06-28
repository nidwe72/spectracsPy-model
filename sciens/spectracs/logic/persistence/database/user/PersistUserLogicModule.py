from typing import List, Optional

from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser
from sciens.spectracs.model.databaseEntity.application.user.AppUserRole import AppUserRole
from sciens.spectracs.model.databaseEntity.application.user.AppUserToAppUserRole import AppUserToAppUserRole


class PersistUserLogicModule:

    def findUserByUsername(self, username: str) -> Optional[AppUser]:
        session = server_session_factory()
        return session.query(AppUser).filter(AppUser.username == username).first()

    def findRoleByName(self, name: str) -> Optional[AppUserRole]:
        session = server_session_factory()
        return session.query(AppUserRole).filter(AppUserRole.name == name).first()

    def getRoleNamesForUser(self, appUser: AppUser) -> List[str]:
        session = server_session_factory()
        links = session.query(AppUserToAppUserRole).filter(
            AppUserToAppUserRole.app_user_id == appUser.id).all()
        result: List[str] = []
        for link in links:
            role = session.query(AppUserRole).filter(AppUserRole.id == link.app_user_role_id).first()
            if role is not None:
                result.append(role.name)
        return result

    def saveUser(self, appUser: AppUser):
        session = server_session_factory()
        session.add(appUser)
        session.commit()

    def saveRole(self, appUserRole: AppUserRole):
        session = server_session_factory()
        session.add(appUserRole)
        session.commit()

    def saveUserToRole(self, appUserToAppUserRole: AppUserToAppUserRole):
        session = server_session_factory()
        session.add(appUserToAppUserRole)
        session.commit()
