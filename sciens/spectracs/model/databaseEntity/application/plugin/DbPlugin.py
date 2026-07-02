from sqlalchemy import Column, String

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class DbPlugin(ServerDbBaseEntity, DbBaseEntityMixin):
    # A registered plugin the master authors; end-users run their bound plugin (concept §9.5 / §11).
    # SERVER-side (same DB as AppUser) so AppUser.pluginId is a real FK. `codeRef` = the import path of the
    # SpectralPlugin subclass — imported by the host CLIENT after login, never executed from the DB, and
    # not signature-verified yet (§11 deferred). Tablename derives to "db_plugin".
    # (SPEC_pumpkin_integration.md B.1 / D5 / D7)

    title = Column(String)
    codeRef = Column(String)
    version = Column(String)
    pdfRef = Column(String)
