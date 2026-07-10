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
