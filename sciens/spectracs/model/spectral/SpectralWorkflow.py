import uuid

from sqlalchemy import Column, String
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
