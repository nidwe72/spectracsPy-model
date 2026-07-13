import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_keyed_dict

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin


class SpectralWorkflowPhase(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (Option A). A phase of the run; its steps are plugin-created (keyed by id).

    workflowId = Column(String, ForeignKey('spectral_workflow.id'))
    type = Column(String)

    steps = relationship("SpectralWorkflowStep", collection_class=attribute_keyed_dict('id'),
                         cascade="all, delete-orphan", back_populates="phase")
    workflow = relationship("SpectralWorkflow", back_populates="phases")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        self._transientHint = None  # SPEC_acquisition_guidance: plugin-authored coach hint for this phase

    def getType(self): return self.type
    def setType(self, phaseType): self.type = phaseType
    def getWorkflow(self): return self.workflow
    def setWorkflow(self, workflow): self.workflow = workflow
    def getSteps(self): return self.steps
    def setSteps(self, steps):
        self.steps.clear()
        for step in steps.values():
            self.addToSteps(step)
    def addToSteps(self, step):
        self.steps[step.getId()] = step
    def getId(self): return self.id
    def setId(self, id): self.id = id
    # SPEC_acquisition_guidance §2 — an optional coach-line hint the PLUGIN authors in its phase hook; the host
    # shows it on phase entry. Transient (not a DB column): guidance is a live-run concern. getattr-guarded so a
    # DB-loaded phase (which bypasses __init__) returns None rather than raising.
    def setHint(self, hint):
        self._transientHint = hint
        return self
    def getHint(self): return getattr(self, "_transientHint", None)
