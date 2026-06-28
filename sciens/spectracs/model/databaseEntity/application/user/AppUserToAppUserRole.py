from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class AppUserToAppUserRole(ServerDbBaseEntity, DbBaseEntityMixin):

    app_user_id: Mapped[str] = Column(ForeignKey("app_user.id"), primary_key=True)

    app_user_role_id: Mapped[str] = Column(ForeignKey("app_user_role.id"), primary_key=True)

    appUserRole: Mapped["AppUserRole"] = relationship("AppUserRole")
