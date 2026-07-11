import base64
from datetime import datetime
from typing import Dict, Optional

from sciens.spectracs.logic.lims.LimsError import LimsError
from sciens.spectracs.logic.lims.LimsGatewayFactory import LimsGatewayFactory
from sciens.spectracs.logic.lims.dto.LimsSubmission import (
    LimsAnalysis, LimsCustomer, LimsInstrument, LimsReport, LimsSample, LimsSampleType, LimsSubmission)
from sciens.spectracs.logic.lims.dto.LimsTarget import LimsTarget
from sciens.spectracs.logic.persistence.database.spectrometerSetup.PersistSpectrometerSetupLogicModule import \
    PersistSpectrometerSetupLogicModule
from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule


class LimsLogicModule:
    """Server-side LIMS publish orchestration (SPEC_lims_integration.md §2/§3, L1-RPC).

    The client sends only its plugin slice (`pluginLimsInfo` = sampleType + analyses + LimsTarget) and the
    M2 PDF (base64). This module resolves the authenticated AppUser + its registered spectrometer graph
    from the server DB to fill the identity half (customer + instrument) — server-authoritative, so the
    client cannot spoof who a sample belongs to. It then picks the LIMS adapter the plugin asked for and
    submits. Returns plain, Pyro-serializable dicts only.
    """

    def publishSample(self, userId, pluginLimsInfo: Dict, pdfBase64: str) -> Dict:
        appUser = PersistUserLogicModule().findUserById(userId)
        if appUser is None:
            return {"ok": False, "message": "user not found"}
        if not appUser.enabled:
            return {"ok": False, "message": "user is disabled"}

        if not pluginLimsInfo or not pluginLimsInfo.get("target"):
            return {"ok": False, "message": "plugin did not declare a LIMS target"}

        # Instrument identity — server-authoritative from the registered spectrometer (SPEC §9).
        serial = appUser.registeredSerial
        if not serial:
            return {"ok": False, "message": "no spectrometer bound to this user"}
        setup = PersistSpectrometerSetupLogicModule().resolveBySerial(serial)
        spectrometer = None
        if setup is not None and setup.spectrometerProfile is not None:
            spectrometer = setup.spectrometerProfile.spectrometer
        if spectrometer is None:
            return {"ok": False, "message": "instrument not resolvable for serial %s" % serial}

        try:
            pdfBytes = base64.b64decode(pdfBase64) if pdfBase64 else b""
        except Exception:
            return {"ok": False, "message": "report payload was not valid base64"}

        submission = self.buildSubmission(appUser, setup, pluginLimsInfo, pdfBytes)

        try:
            gateway = LimsGatewayFactory.create(submission.target)
            ref = gateway.submit(submission)
        except LimsError as error:
            print("LimsLogicModule.publishSample LIMS error: %s (%s)" % (error, error.detail))
            return {"ok": False, "message": "LIMS error: %s" % error}

        return {"ok": True, "sampleId": ref.sampleId, "url": ref.url, "message": None}

    # --- pure assembly (no DB, unit-testable) -------------------------------
    def buildSubmission(self, appUser, setup, pluginLimsInfo: Dict, pdfBytes: bytes) -> LimsSubmission:
        customer = LimsCustomer(
            code=appUser.username,                                  # stable idempotency key
            name=appUser.displayName or appUser.username,
            contactFirst=appUser.firstName or "",
            contactLast=appUser.lastName or "",
            email=appUser.email or "")

        profile = setup.spectrometerProfile
        spectrometer = profile.spectrometer
        vendor = getattr(spectrometer, "spectrometerVendor", None)
        style = getattr(spectrometer, "spectrometerStyle", None)
        sensor = getattr(spectrometer, "spectrometerSensor", None)
        # Fall back to non-empty labels so the LIMS never gets blank-title master data (an incompletely
        # populated spectrometer graph would otherwise yield empty Manufacturer/Supplier titles).
        instrument = LimsInstrument(
            serial=profile.serial,
            model=spectrometer.modelName or "Spectracs",
            manufacturer=(vendor.vendorName if vendor is not None else "") or "Spectracs",
            kind=(style.styleName if style is not None else "") or "Spectrometer",
            supplier=(sensor.sellerName if sensor is not None else "") or "Spectracs")

        sampleTypeInfo = pluginLimsInfo.get("sampleType") or {}
        sampleType = LimsSampleType(sampleTypeInfo.get("name", "Sample"),
                                    sampleTypeInfo.get("code", "SMP"))

        analyses = [LimsAnalysis(a.get("name", ""), a.get("key", ""), a.get("group", ""))
                    for a in (pluginLimsInfo.get("analyses") or [])]

        targetInfo = pluginLimsInfo["target"]
        target = LimsTarget(targetInfo.get("backend"), targetInfo.get("configKey"))

        dateIso = pluginLimsInfo.get("dateSampledIso") or datetime.utcnow().isoformat()
        sample = LimsSample(dateIso, pluginLimsInfo.get("externalId"))

        fileName = pluginLimsInfo.get("pdfFileName") or ("%s-report.pdf" % sampleType.code)
        report = LimsReport(bytes(pdfBytes) if pdfBytes else b"", fileName)

        return LimsSubmission(customer, instrument, sampleType, analyses, sample, report, target)
