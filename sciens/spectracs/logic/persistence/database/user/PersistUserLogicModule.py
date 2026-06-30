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

    def findUserById(self, userId: str) -> Optional[AppUser]:
        session = server_session_factory()
        return session.query(AppUser).filter(AppUser.id == userId).first()

    def listAllUsers(self) -> List[AppUser]:
        session = server_session_factory()
        return session.query(AppUser).all()

    def updateUser(self, appUser: AppUser):
        session = server_session_factory()
        session.merge(appUser)
        session.commit()

    def deleteUser(self, userId: str):
        # Hard delete: remove the user's role links first, then the user row.
        session = server_session_factory()
        session.query(AppUserToAppUserRole).filter(
            AppUserToAppUserRole.app_user_id == userId).delete()
        session.query(AppUser).filter(AppUser.id == userId).delete()
        session.commit()

    def replaceUserRoles(self, appUser: AppUser, roleNames: List[str]):
        # Drop the user's existing role links, then re-create one per given role name.
        session = server_session_factory()
        session.query(AppUserToAppUserRole).filter(
            AppUserToAppUserRole.app_user_id == appUser.id).delete()
        session.commit()
        for roleName in roleNames:
            role = self.findRoleByName(roleName)
            if role is not None:
                link = AppUserToAppUserRole()
                link.app_user_id = appUser.id
                link.app_user_role_id = role.id
                self.saveUserToRole(link)

    def countUsersWithRole(self, roleName: str) -> int:
        # Counts ENABLED users holding the role — used for the last-master-user guard.
        session = server_session_factory()
        role = self.findRoleByName(roleName)
        if role is None:
            return 0
        links = session.query(AppUserToAppUserRole).filter(
            AppUserToAppUserRole.app_user_role_id == role.id).all()
        count = 0
        for link in links:
            user = session.query(AppUser).filter(AppUser.id == link.app_user_id).first()
            if user is not None and user.enabled:
                count += 1
        return count
