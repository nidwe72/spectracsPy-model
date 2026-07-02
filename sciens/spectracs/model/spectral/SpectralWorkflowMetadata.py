import uuid

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin


class SpectralWorkflowMetadata(DbBaseEntity, DbBaseEntityMixin):
    # A plugin-declared, self-describing metadata field row (EAV) — child of SpectralWorkflow
    # (SPEC_workflow_persistence.md §2.3). `showInWorkflowsTable` -> the field is a column in the Home list.

    workflowId = Column(String, ForeignKey('spectral_workflow.id'))
    name = Column(String)
    label = Column(String)
    type = Column(String)          # TEXT | NUMBER | DATE
    value = Column(String)         # DATE = ISO yyyy-mm-dd
    showInWorkflowsTable = Column(Boolean, default=False)
    order = Column(Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
