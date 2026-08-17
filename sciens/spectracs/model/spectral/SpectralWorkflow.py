import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.orm.collections import attribute_keyed_dict

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.spectral.SpectralWorkflowPhaseType import SpectralWorkflowPhaseType


class SpectralWorkflow(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (Option A / concept §9.5) — the workflow IS the persisted record. Run
    # metadata (username/userId/pluginCodeRef/timestampIso) is stamped at Save. `currentPhase` is transient.

    username = Column(String)
    userId = Column(String)
    pluginCodeRef = Column(String)
    pluginVersion = Column(String)  # A3 provenance: the EXACT resolved plugin version; NULL -> shipped built-in
    timestampIso = Column(String)
    # SPEC_settled_measurement.md §15.2 — the monitored acquisition's own record: outcome, branch, how the
    # answer was read, the clearing time, the DECISION ROWS, and the policy + evaluator version it ran
    # under. NULL for every plain-burst capture, which is most of them.
    #
    # ⭐ ONE TEXT COLUMN, holding the plugin's SELF-DESCRIBING structure (`columns` + `rows` + `answer`).
    # ⛔ Not a table of typed columns: `qPercent / soret / valley / qBand` would hard-code one plugin's
    # physics into the app's schema — the exact mistake §10.1a-bis removed from the SDK, and the reason
    # §15.2 insists the host know only `t` and `answer["valueKey"]`.
    # ⚠ Rows are a JSON LIST of objects with `t` as a VALUE, never a map keyed by a float: JSON turns
    # float keys into strings on the way back (SPEC_workflow_persistence.md's float-key gotcha).
    monitorRecordJson = Column(Text)
    # ⭐⭐ SPEC_settled_measurement.md §27.14a (D4) — WHICH PHASES ARE SECTIONED BY STEP: the phases whose
    # steps are sections in their own right ("Reference" / "Sample" rather than one "Acquisition").
    #
    # ⭐ THE PLUGIN DECLARES IT, THE RECORD CARRIES IT. It arrives from the plugin's
    # `NavigationPolicy.stepChevronPhases` and is stamped at run start, after which EVERY consumer reads it
    # from the workflow: the chevron, a RE-OPENED run, the PDF's section headings, a LIMS addon rebuilding a
    # report with no plugin loaded. ⛔ Before this the declaration lived only in the live host, so a
    # re-opened measurement navigated differently from the way it was measured.
    # ⚠ It is the STRUCTURAL half of the navigation policy only. ⛔ `mode` (STEP / AUTO_ADVANCE) is NOT
    # persisted: re-opening a run is browsing, not measuring, and auto-advance is not a fact about the
    # measurement.
    # ⚠ Stored as a SORTED JSON list of enum values — a frozenset's iteration order must never reach the
    # blob, or two identical runs produce different bytes (§27.16/N4).
    sectionedPhasesJson = Column(Text)

    phases = relationship("SpectralWorkflowPhase", collection_class=attribute_keyed_dict('type'),
                          cascade="all, delete-orphan", back_populates="workflow")
    metadataFields = relationship("SpectralWorkflowMetadata", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        self.__initTransient()

    @reconstructor
    def __initTransient(self):
        self.currentPhase = None

    def getMonitorRecord(self):
        # SPEC_settled_measurement.md §15.2 — the settling trajectory as the plugin declared it, or None
        # for a plain-burst capture. Parsed lazily: most runs never look at it.
        import json
        if not self.monitorRecordJson:
            return None
        try:
            return json.loads(self.monitorRecordJson)
        except (TypeError, ValueError):
            return None

    def setMonitorRecord(self, record):
        # ⚠ `record` is MonitorResult.toRecord() — plain JSON-able types only, rows as a LIST.
        import json
        self.monitorRecordJson = None if record is None else json.dumps(record)

    def getSectionedPhases(self):
        # D4 (§27.14a) — the phases whose STEPS are sections. Returns a frozenset of
        # SpectralWorkflowPhaseType; empty for every run made before D4, which reads as "no sub-sections"
        # and is exactly the pre-D4 behaviour (§27.16/N5).
        import json
        if not self.sectionedPhasesJson:
            return frozenset()
        try:
            values = json.loads(self.sectionedPhasesJson)
        except (TypeError, ValueError):
            return frozenset()
        known = {member.value: member for member in SpectralWorkflowPhaseType}
        return frozenset(known[value] for value in values if value in known)  # unknown tags: dropped, not fatal

    def setSectionedPhases(self, phaseTypes):
        # ⚠ SORTED on the way in (§27.16/N4): the caller hands a frozenset, whose iteration order is a hash
        # detail — letting it reach the column would make two identical runs differ byte for byte.
        import json
        values = sorted(getattr(phaseType, "value", str(phaseType)) for phaseType in (phaseTypes or ()))
        self.sectionedPhasesJson = json.dumps(values) if values else None

    def getPhases(self): return self.phases
    def setPhases(self, phases):
        self.phases.clear()
        for phase in phases.values():
            self.addToPhases(phase)
    def addToPhases(self, phase):
        self.phases[phase.getType()] = phase
        phase.setWorkflow(self)
    def getPhase(self, spectralWorkflowPhaseType):
        return self.phases.get(spectralWorkflowPhaseType)
    def getAcquireViewPhase(self):
        return self.getPhase(SpectralWorkflowPhaseType.ACQUIREMENT_VIEW)

    # --- report serialization (SPEC_bench_pdf_export.md §5, D3) — the WHOLE workflow as the machine-readable
    # LIS payload embedded in the PDF: run header + every phase -> step -> (its SpectraContainer spectra
    # {nm:value} + its EvaluationResult view-models + any serializable passive view). Complete provenance, raw
    # acquisition through verdict. Distinct from the *visible* report (the isShownInReport subset). Captured
    # image PIXELS are NOT here (§5b) — the SpectrumCaptureView descriptor carries only its attachmentName; the
    # image travels as a named PDF attachment. ---
    def toReportJson(self):
        phases = []
        for phaseType in SpectralWorkflowPhaseType:
            phase = self.getPhase(phaseType)
            if phase is None:
                continue
            steps = []
            for step in phase.getSteps().values():
                steps.append(self.__stepReportJson(step))
            phases.append({"type": getattr(phaseType, "value", str(phaseType)), "steps": steps})
        return {
            "header": {"username": self.username, "userId": self.userId,
                       "pluginCodeRef": self.pluginCodeRef, "pluginVersion": self.pluginVersion,
                       "timestampIso": self.timestampIso},
            # ⭐ HOW THE VALUE WAS CHOSEN travels with the document (SPEC_settled_measurement.md §15.2 /
            # §27.11). Without it a PDF from a monitored run carried the answer but not the trajectory,
            # the gate's own numbers, or the policy the run was made under — and §5's promise is
            # "complete provenance, raw acquisition through verdict". None for a plain-burst capture.
            "monitorRecord": self.getMonitorRecord(),
            # ⭐ D4 (§27.14a / §27.16-N3): the section structure travels with the DOCUMENT too, not only in
            # the DB column — `diagnostics/report_reconstruct.py` and a LIMS addon rebuild a workflow from
            # this JSON with no database and no plugin, and they must lay it out the way it was measured.
            # ⚠ Absent in every report written before D4 ⇒ reconstructs as "no sub-sections".
            "sectionedPhases": sorted(phaseType.value for phaseType in self.getSectionedPhases()),
            "phases": phases,
        }

    @staticmethod
    def __stepReportJson(step):
        entry = {"id": step.getId(), "role": step.getRole(), "label": step.getLabel(),
                 "spectra": {}, "items": []}
        container = step.getContainer()
        if container is not None:
            entry["spectra"] = {role: spectrum.toJson()
                                for role, spectrum in container.getSpectra().items()}
        result = step.getEvaluationResult()
        if result is not None:
            entry["items"].extend(item.toJson() for item in result.getItems() if hasattr(item, "toJson"))
        view = step.getView() if hasattr(step, "getView") else None
        if view is not None and hasattr(view, "toJson"):  # passive SpectrumPlotView/SpectrumCaptureView; skips
            entry["items"].append(view.toJson())          # the interactive CaptureView / the ReportView (no toJson)
        return entry

    def getMetadataFields(self):
        return self.metadataFields
    def setMetadataFields(self, fields):
        self.metadataFields.clear()
        for field in fields:
            self.metadataFields.append(field)
    def addToMetadataFields(self, field):
        self.metadataFields.append(field)


# --- Registration hub: importing SpectralWorkflow registers the whole graph so configure_mappers() can
# resolve every string relationship regardless of which module was imported first. (Siblings import only
# DbBase + leaf types, so there is no cycle.)
from sciens.spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase  # noqa: E402,F401
from sciens.spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep  # noqa: E402,F401
from sciens.spectracs.model.spectral.SpectraContainer import SpectraContainer  # noqa: E402,F401
from sciens.spectracs.model.spectral.Spectrum import Spectrum  # noqa: E402,F401
from sciens.spectracs.model.spectral.SpectralWorkflowMetadata import SpectralWorkflowMetadata  # noqa: E402,F401
from sciens.spectracs.model.spectral.plugin.view.EvaluationResult import EvaluationResult  # noqa: E402,F401
