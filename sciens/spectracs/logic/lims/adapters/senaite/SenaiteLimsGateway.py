import base64
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

from sciens.spectracs.logic.config.ServerConfig import ServerConfig
from sciens.spectracs.logic.lims.LimsError import LimsError
from sciens.spectracs.logic.lims.LimsGateway import LimsGateway
from sciens.spectracs.logic.lims.dto.LimsHealth import LimsHealth
from sciens.spectracs.logic.lims.dto.LimsSampleRef import LimsSampleRef
from sciens.spectracs.logic.lims.dto.LimsSubmission import LimsSubmission


class SenaiteLimsGateway(LimsGateway):
    """SENAITE adapter over `senaite.jsonapi` (SPEC_lims_integration.md §5/§6). Reads its base URL + Basic
    creds from the server `.env` via `ServerConfig`, keyed by `configKey` (LIMS_<configKey>_BASE_URL/
    _USER/_PASSWORD). Stdlib-only HTTP (urllib), like `PayPalGateway`.

    Maps the LIMS-neutral `LimsSubmission` onto SENAITE's object graph, ensuring/creating every prerequisite
    idempotently (search by a stable key first, create only if absent), then creates the AnalysisRequest and
    attaches the PDF.
    """

    # Plone container paths per portal_type — discovered on SENAITE 2.6.0 (note: AnalysisService + Instrument
    # sit under the legacy bika_setup, the rest under setup). Version-specific; verified against the instance.
    CONTAINERS = {
        "Client": "/senaite/clients",
        "SampleType": "/senaite/setup/sampletypes",
        "Department": "/senaite/setup/departments",
        "AnalysisCategory": "/senaite/setup/analysiscategories",
        "AnalysisService": "/senaite/bika_setup/bika_analysisservices",
        "InstrumentType": "/senaite/setup/instrumenttypes",
        "Manufacturer": "/senaite/setup/manufacturers",
        "Supplier": "/senaite/setup/suppliers",
        "Instrument": "/senaite/bika_setup/bika_instruments",
    }

    def __init__(self, configKey: str = "SENAITE"):
        self.configKey = configKey
        self._base = (ServerConfig.get("LIMS_%s_BASE_URL" % configKey, "") or "").rstrip("/")
        self._user = ServerConfig.get("LIMS_%s_USER" % configKey, "") or ""
        self._password = ServerConfig.get("LIMS_%s_PASSWORD" % configKey, "") or ""

    # --- LimsGateway ---------------------------------------------------------
    def checkConnection(self) -> LimsHealth:
        if not self._base:
            return LimsHealth(False, "LIMS_%s_BASE_URL not configured" % self.configKey)
        try:
            response = self._request("GET", "/users/current")
        except LimsError as error:
            return LimsHealth(False, "cannot reach SENAITE: %s" % error, error.detail)
        items = response.get("items") or []
        authed = bool(items and items[0].get("authenticated"))
        if not authed:
            return LimsHealth(False, "SENAITE reachable but credentials not accepted")
        return LimsHealth(True, "authenticated as %s" % items[0].get("username"))

    def submit(self, submission: LimsSubmission) -> LimsSampleRef:
        # Bottom-up ensure-or-create (idempotent), then the sample, then attach the PDF. SENAITE 2.6.0
        # lets an AnalysisService exist with no category, so we skip the Department/Category chain (§5).
        instrument = submission.instrument
        instrumentTypeUid = self._ensure("InstrumentType", instrument.kind,
                                          {"title": instrument.kind}, parentPath=self.CONTAINERS["InstrumentType"])
        manufacturerUid = self._ensure("Manufacturer", instrument.manufacturer,
                                        {"title": instrument.manufacturer}, parentPath=self.CONTAINERS["Manufacturer"])
        supplierUid = self._ensure("Supplier", instrument.supplier,
                                    {"title": instrument.supplier}, parentPath=self.CONTAINERS["Supplier"])
        instrumentTitle = ("%s %s" % (instrument.model, instrument.serial)).strip()
        self._ensure("Instrument", instrumentTitle,
                     {"title": instrumentTitle, "SerialNo": instrument.serial, "Model": instrument.model,
                      "InstrumentType": instrumentTypeUid, "Manufacturer": manufacturerUid,
                      "Supplier": supplierUid}, parentPath=self.CONTAINERS["Instrument"])

        sampleType = submission.sampleType
        sampleTypeUid = self._ensure("SampleType", sampleType.name,
                                     {"title": sampleType.name, "prefix": sampleType.code,
                                      "min_volume": "0 mL"}, parentPath=self.CONTAINERS["SampleType"])

        analysisUids = []
        for analysis in submission.analyses:
            uid = self._ensure("AnalysisService", analysis.name,
                               {"title": analysis.name, "Keyword": analysis.key},
                               parentPath=self.CONTAINERS["AnalysisService"])
            analysisUids.append(uid)

        customer = submission.customer
        clientItem = self._ensureItem("Client", customer.name,
                                      {"title": customer.name, "Name": customer.name,
                                       "ClientID": customer.code}, parentPath=self.CONTAINERS["Client"])
        clientUid = clientItem.get("uid")
        clientPath = clientItem.get("path") or (self.CONTAINERS["Client"] + "/" + (clientItem.get("id") or ""))
        contactUid = self._ensure("Contact", "%s %s" % (customer.contactFirst, customer.contactLast),
                                  {"Firstname": customer.contactFirst, "Surname": customer.contactLast,
                                   "EmailAddress": customer.email}, parentPath=clientPath)

        created = self._createSample(clientUid, contactUid, sampleTypeUid, analysisUids, submission.sample)
        sampleId = created.get("title") or created.get("id")
        url = created.get("url") or created.get("api_url")
        self._attachPdf(created.get("uid"), clientPath, submission.report)
        return LimsSampleRef(sampleId, url)

    # --- ensure-or-create ----------------------------------------------------
    def _ensure(self, portalType: str, matchTitle: str, createFields: Dict, parentPath: str) -> str:
        return self._ensureItem(portalType, matchTitle, createFields, parentPath).get("uid")

    def _ensureItem(self, portalType: str, matchTitle: str, createFields: Dict, parentPath: str) -> Dict:
        """Idempotent: find an object of `portalType` whose title equals `matchTitle`, else create it under
        `parentPath`, then resolve it by title. Title match is in Python (the title index is fuzzy).

        Robust to a SENAITE quirk: some DX creates (e.g. AnalysisService) *persist the object* but return an
        error body (`success:false`, "'NoneType'.form"). So we always resolve by search after creating,
        rather than trusting the create response to carry the uid."""
        found = self._findByTitle(portalType, matchTitle)
        if found is not None:
            return found

        body = {"portal_type": portalType, "parent_path": parentPath}
        body.update(createFields)
        createError = None
        try:
            response = self._request("POST", "/create", body=body)
            if not response.get("items"):
                createError = response.get("message")
        except LimsError as error:
            createError = error.detail or str(error)

        found = self._findByTitle(portalType, matchTitle)
        if found is not None:
            return found
        raise LimsError("could not create %s %r" % (portalType, matchTitle), createError)

    def _findByTitle(self, portalType: str, matchTitle: str) -> Optional[Dict]:
        target = (matchTitle or "").strip()
        for item in self._search(portalType, limit=500):
            if (item.get("title") or "").strip() == target:
                return item
        return None

    def _createSample(self, clientUid, contactUid, sampleTypeUid, analysisUids, sample) -> Dict:
        # DateSampled is sent date-only: SENAITE rejects a DateSampled after "now" (its container clock),
        # so a full timestamp can trip the future-date validation.
        body = {"portal_type": "AnalysisRequest", "parent_uid": clientUid,
                "Contact": contactUid, "SampleType": sampleTypeUid,
                "DateSampled": (sample.dateSampledIso or "")[:10], "Analyses": analysisUids}
        return self._create(body)

    def _attachPdf(self, sampleUid: Optional[str], clientPath: str, report) -> Optional[str]:
        # Attachments must be created under the CLIENT (not the sample), with the file as a plain base64
        # string (the dict/data-uri forms trip an "Incorrect padding" error). The AR<->attachment link is
        # set via updating the sample's Attachment list; this jsonapi build does not read it back, so verify
        # on the sample's Attachments tab. SPEC_lims_integration.md §5 / L5.
        b64 = base64.b64encode(report.pdfBytes or b"").decode("ascii")
        created = self._create({"portal_type": "Attachment", "parent_path": clientPath,
                                "AttachmentFile": b64, "filename": report.fileName})
        attachmentUid = created.get("uid")
        if attachmentUid and sampleUid:
            try:
                self._request("POST", "/update", body={"uid": sampleUid, "Attachment": [attachmentUid]})
            except LimsError:
                pass  # the file is stored under the client even if the AR link is unavailable
        return attachmentUid

    # --- create helpers ------------------------------------------------------
    def _create(self, body: Dict) -> Dict:
        response = self._request("POST", "/create", body=body)
        items = response.get("items") or []
        if not items:
            raise LimsError("SENAITE create returned no item for %s" % body.get("portal_type"), response)
        return items[0]

    # --- search / lookup -----------------------------------------------------
    def _search(self, portalType: str, **filters) -> List[Dict]:
        params = {"portal_type": portalType, "complete": "false"}
        params.update({k: v for k, v in filters.items() if v is not None})
        response = self._request("GET", "/search", params=params)
        return response.get("items") or []

    def _findUid(self, portalType: str, **filters) -> Optional[str]:
        items = self._search(portalType, limit=1, **filters)
        return items[0].get("uid") if items else None

    # --- transport -----------------------------------------------------------
    def _authHeader(self) -> str:
        return "Basic " + base64.b64encode(("%s:%s" % (self._user, self._password)).encode()).decode("ascii")

    def _request(self, method: str, path: str, params: Optional[Dict] = None, body=None) -> Dict:
        url = self._base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Authorization": self._authHeader()}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        context = ssl.create_default_context()
        try:
            with urllib.request.urlopen(request, timeout=30, context=context) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise LimsError("SENAITE HTTP %s on %s" % (error.code, path), detail)
        except urllib.error.URLError as error:
            raise LimsError("SENAITE network error on %s: %s" % (path, error.reason))
        if raw == "":
            return {}
        try:
            return json.loads(raw)
        except Exception:
            raise LimsError("SENAITE returned non-JSON on %s" % path, {"raw": raw[:300]})
