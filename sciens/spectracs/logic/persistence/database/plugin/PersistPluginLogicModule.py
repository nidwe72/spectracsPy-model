from typing import Optional

from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.application.plugin.DbPlugin import DbPlugin


class PersistPluginLogicModule:
    # Server-side persistence for the DbPlugin registry (SPEC_pumpkin_integration.md B.1a).

    def findPluginByCodeRef(self, codeRef: str) -> Optional[DbPlugin]:
        session = server_session_factory()
        return session.query(DbPlugin).filter(DbPlugin.codeRef == codeRef).first()

    def savePlugin(self, dbPlugin: DbPlugin):
        session = server_session_factory()
        session.add(dbPlugin)
        session.commit()

    def getOrCreate(self, title: str, codeRef: str, version: str, pdfRef: str = None) -> DbPlugin:
        # Idempotent (mirrors the skip-if-exists user seed): keyed on codeRef.
        existing = self.findPluginByCodeRef(codeRef)
        if existing is not None:
            return existing
        dbPlugin = DbPlugin()
        dbPlugin.title = title
        dbPlugin.codeRef = codeRef
        dbPlugin.version = version
        dbPlugin.pdfRef = pdfRef
        self.savePlugin(dbPlugin)
        return dbPlugin
