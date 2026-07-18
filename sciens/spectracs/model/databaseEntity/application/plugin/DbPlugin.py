from sqlalchemy import Column, String, Text, Integer, UniqueConstraint

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class DbPlugin(ServerDbBaseEntity, DbBaseEntityMixin):
    # A registered plugin the master authors; end-users run their bound plugin (concept §9.5 / §11).
    # SERVER-side. `codeRef` = the import path of the SpectralPlugin subclass. Tablename derives to "db_plugin".
    #
    # B0 (SPEC_plugin_distribution.md §1): identity is **(codeRef, version)** — one immutable row per published
    # version, INSERT-never-upsert. The uuid `id` stays the PK (the SpectrometerSetup.pluginId FK points at a
    # specific row). The mixin already sets __table_args__ = {'extend_existing': True}; we override it with a
    # tuple that ADDS the unique constraint AND preserves that flag.
    __table_args__ = (
        UniqueConstraint("codeRef", "version", name="uq_db_plugin_coderef_version"),
        {"extend_existing": True},
    )

    title = Column(String)
    codeRef = Column(String)
    version = Column(String)
    pdfRef = Column(String)

    # B1 — signed-distribution payload (SPEC_plugin_distribution.md §5 / §8). Null until a version is published
    # (B4); the client fetches source+signature over getPluginSource, verifies the tuple, then execs (B3).
    source = Column(Text)               # the plugin's single-module Python source
    signature = Column(String)          # base64 Ed25519 signature over codeRef|version|targetSdkVersion|sha256(source)
    keyId = Column(String)              # which TRUSTED_KEYS pubkey signed it (fingerprint = sha256(pubkey)[:16])
    author = Column(String)             # the master username that published it
    targetSdkVersion = Column(Integer)  # plugin_sdk version the source was built against (A2)
