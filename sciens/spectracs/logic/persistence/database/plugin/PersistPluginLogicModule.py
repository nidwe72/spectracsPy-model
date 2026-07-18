from typing import List, Optional

from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.application.plugin.DbPlugin import DbPlugin


class PersistPluginLogicModule:
    # Server-side persistence for the DbPlugin registry. B0 (SPEC_plugin_distribution.md §1): identity is
    # (codeRef, version) — one immutable row per published version, **INSERT-never-upsert**. The old
    # upsert()-on-codeRef is gone: overwriting a row would move every instrument pointed at it at once.

    def findPluginByCodeRef(self, codeRef: str) -> Optional[DbPlugin]:
        # Legacy single-row lookup (fine while a codeRef has one version). Version-sensitive callers use
        # findByCodeRefAndVersion; B5 moves the assign path off the ambiguous `.first()`.
        session = server_session_factory()
        return session.query(DbPlugin).filter(DbPlugin.codeRef == codeRef).first()

    def findByCodeRefAndVersion(self, codeRef: str, version: str) -> Optional[DbPlugin]:
        session = server_session_factory()
        return session.query(DbPlugin).filter(
            DbPlugin.codeRef == codeRef, DbPlugin.version == version).first()

    def listPlugins(self) -> List[DbPlugin]:
        session = server_session_factory()
        return session.query(DbPlugin).all()

    def savePlugin(self, dbPlugin: DbPlugin):
        session = server_session_factory()
        session.add(dbPlugin)
        session.commit()

    def getOrCreate(self, title: str, codeRef: str, version: str, pdfRef: str = None) -> DbPlugin:
        # Idempotent per (codeRef, version) — the seed re-runs safely on every server start.
        existing = self.findByCodeRefAndVersion(codeRef, version)
        if existing is not None:
            return existing
        return self._insert(title, codeRef, version, pdfRef)

    def createVersion(self, title: str, codeRef: str, version: str, pdfRef: str = None,
                      source: str = None, signature: str = None, keyId: str = None,
                      author: str = None, targetSdkVersion: int = None) -> DbPlugin:
        # Publish: INSERT one (codeRef, version) row. A published row is immutable and never overwritten —
        # re-publishing an existing version is refused (raises), not an upsert. The sealed columns are filled
        # by the publish path (B4/B2); they stay null for a plain title/codeRef/version row.
        if self.findByCodeRefAndVersion(codeRef, version) is not None:
            raise ValueError("plugin %s version %s is already published" % (codeRef, version))
        return self._insert(title, codeRef, version, pdfRef,
                            source, signature, keyId, author, targetSdkVersion)

    def _insert(self, title, codeRef, version, pdfRef,
                source=None, signature=None, keyId=None, author=None, targetSdkVersion=None) -> DbPlugin:
        dbPlugin = DbPlugin()
        dbPlugin.title = title
        dbPlugin.codeRef = codeRef
        dbPlugin.version = version
        dbPlugin.pdfRef = pdfRef
        dbPlugin.source = source
        dbPlugin.signature = signature
        dbPlugin.keyId = keyId
        dbPlugin.author = author
        dbPlugin.targetSdkVersion = targetSdkVersion
        self.savePlugin(dbPlugin)
        return dbPlugin
