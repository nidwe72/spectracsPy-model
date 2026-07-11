from typing import List, Optional

from sciens.spectracs.logic.lims.dto.LimsTarget import LimsTarget


class LimsCustomer:
    """The customer a sample belongs to. Server-filled from the authenticated AppUser
    (SPEC_lims_integration.md §3/§4) — the client never supplies it. `code` is the stable
    idempotency key (derived from `username`), `name` the display title."""

    def __init__(self, code: str, name: str, contactFirst: str = "", contactLast: str = "",
                 email: str = ""):
        self.code = code
        self.name = name
        self.contactFirst = contactFirst
        self.contactLast = contactLast
        self.email = email

    def toDict(self) -> dict:
        return {"code": self.code, "name": self.name, "contactFirst": self.contactFirst,
                "contactLast": self.contactLast, "email": self.email}


class LimsInstrument:
    """The measuring device. Server-filled from the registered spectrometer graph
    (AppUser.registeredSerial -> SpectrometerProfile -> Spectrometer/Vendor/Style/Sensor). `serial`
    is the idempotency key."""

    def __init__(self, serial: str, model: str = "", manufacturer: str = "", kind: str = "",
                 supplier: str = ""):
        self.serial = serial
        self.model = model
        self.manufacturer = manufacturer
        self.kind = kind                # instrument type / category
        self.supplier = supplier

    def toDict(self) -> dict:
        return {"serial": self.serial, "model": self.model, "manufacturer": self.manufacturer,
                "kind": self.kind, "supplier": self.supplier}


class LimsSampleType:
    """The kind of material sampled (e.g. "Pumpkin Oil" / "OIL"). Plugin-supplied."""

    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code                # short prefix, drives the sample id (OIL-0001)

    def toDict(self) -> dict:
        return {"name": self.name, "code": self.code}


class LimsAnalysis:
    """A test/analysis to record on the sample. Plugin-supplied. M1 sends a single generic analysis
    ("Spectracs Measurement") — the milestone is data upload; real per-metric analyses come later via a
    LIMS-side plugin (SPEC §3/§11). `key` is the stable keyword; `group` its category."""

    def __init__(self, name: str, key: str, group: str = ""):
        self.name = name
        self.key = key
        self.group = group

    def toDict(self) -> dict:
        return {"name": self.name, "key": self.key, "group": self.group}


class LimsSample:
    """The sample event itself."""

    def __init__(self, dateSampledIso: str, externalId: Optional[str] = None):
        self.dateSampledIso = dateSampledIso
        self.externalId = externalId    # our workflow/run id, optional

    def toDict(self) -> dict:
        return {"dateSampledIso": self.dateSampledIso, "externalId": self.externalId}


class LimsReport:
    """The client-built M2 PDF to attach (bytes + filename). Not serialized into toDict (binary)."""

    def __init__(self, pdfBytes: bytes, fileName: str):
        self.pdfBytes = pdfBytes
        self.fileName = fileName

    def toDict(self) -> dict:
        size = len(self.pdfBytes) if self.pdfBytes is not None else 0
        return {"fileName": self.fileName, "bytes": size}


class LimsSubmission:
    """The complete, LIMS-neutral request assembled server-side and handed to a `LimsGateway`.
    Uses our vocabulary only — no LIMS terms leak above the adapter (SPEC_lims_integration.md §3)."""

    def __init__(self, customer: LimsCustomer, instrument: LimsInstrument,
                 sampleType: LimsSampleType, analyses: List[LimsAnalysis], sample: LimsSample,
                 report: LimsReport, target: LimsTarget):
        self.customer = customer
        self.instrument = instrument
        self.sampleType = sampleType
        self.analyses = analyses
        self.sample = sample
        self.report = report
        self.target = target

    def toDict(self) -> dict:
        """Loggable view — omits the raw PDF bytes."""
        return {"customer": self.customer.toDict(), "instrument": self.instrument.toDict(),
                "sampleType": self.sampleType.toDict(),
                "analyses": [a.toDict() for a in self.analyses],
                "sample": self.sample.toDict(), "report": self.report.toDict(),
                "target": self.target.toDict()}

    def __repr__(self) -> str:
        return "LimsSubmission(%r)" % (self.toDict(),)
