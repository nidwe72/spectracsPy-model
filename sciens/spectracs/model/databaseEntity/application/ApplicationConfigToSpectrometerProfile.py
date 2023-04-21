from sqlalchemy import ForeignKey, Column, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
# from sqlalchemy.orm import MappedColumn

import sqlalchemy.orm



# from sqlalchemy.orm._orm_constructors import mapped_column
from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin

class ApplicationConfigToSpectrometerProfile(DbBaseEntity,DbBaseEntityMixin):

    isDefault = Column('isDefault', Boolean, default=False)

    # application_config_id: Mapped[str] = mapped_column(ForeignKey("application_config.id"), primary_key=True)

    # spectrometer_profile_id: Mapped[str] = mapped_column(
    #     ForeignKey("spectrometer_profile.id"), primary_key=True
    # )


    application_config_id: Mapped[str] = Column(ForeignKey("application_config.id"), primary_key=True)

    spectrometer_profile_id: Mapped[str] = Column(
        ForeignKey("spectrometer_profile.id"), primary_key=True
    )


    spectrometerProfile: Mapped["SpectrometerProfile"] = relationship("SpectrometerProfile")


