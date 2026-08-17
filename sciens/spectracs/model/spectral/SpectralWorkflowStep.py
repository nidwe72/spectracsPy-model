import uuid

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship, reconstructor

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin


class SpectralWorkflowStep(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (Option A). Carries one unit of work: a spectra container and/or an
    # evaluation result (both cascade children). `view`/`widget` are host-built TRANSIENT (never mapped).

    phaseId = Column(String, ForeignKey('spectral_workflow_phase.id'))
    role = Column(String)
    label = Column(String)
    frames = Column(Integer)
    mandatory = Column(Boolean, default=False)
    persist = Column(Boolean, default=False)

    container = relationship("SpectraContainer", uselist=False, back_populates="producedBy",
                             cascade="all, delete-orphan")
    evaluationResult = relationship("EvaluationResult", uselist=False, cascade="all, delete-orphan")
    phase = relationship("SpectralWorkflowPhase", back_populates="steps")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.mandatory is None:
            self.mandatory = False
        if self.persist is None:
            self.persist = False
        self.__initTransient()

    @reconstructor
    def __initTransient(self):
        self._view = None
        self._widget = None

    def getPhase(self): return self.phase
    def setPhase(self, phase): self.phase = phase
    def getId(self): return self.id
    def setId(self, id): self.id = id
    def getContainer(self): return self.container
    def setContainer(self, container): self.container = container
    def getEvaluationResult(self): return self.evaluationResult
    def setEvaluationResult(self, evaluationResult): self.evaluationResult = evaluationResult
    def getView(self): return self._view
    def setView(self, view): self._view = view
    def getWidget(self): return self._widget
    def setWidget(self, widget): self._widget = widget
    def getPersist(self): return self.persist
    def setPersist(self, persist): self.persist = persist
    def getRole(self): return self.role
    def setRole(self, role): self.role = role
    def getLabel(self): return self.label
    def setLabel(self, label): self.label = label
    def getFrames(self): return self.frames
    def setFrames(self, frames): self.frames = frames
    def getMandatory(self): return self.mandatory
    def setMandatory(self, mandatory): self.mandatory = mandatory
