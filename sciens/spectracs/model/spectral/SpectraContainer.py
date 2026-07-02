import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.orm.collections import attribute_keyed_dict

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin


class SpectraContainer(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (Option A). One stage of a run: named bags of spectra keyed by role
    # (attribute_keyed_dict). `producedBy` = the step that owns it. `inputs` (provenance) stays TRANSIENT
    # for now (SPEC_workflow_persistence.md §9 out-of-scope).

    stepId = Column(String, ForeignKey('spectral_workflow_step.id'))

    _spectra = relationship("Spectrum", collection_class=attribute_keyed_dict('role'),
                            cascade="all, delete-orphan")
    producedBy = relationship("SpectralWorkflowStep", back_populates="container")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        self.__initTransient()

    @reconstructor
    def __initTransient(self):
        self._inputs = []

    def getSpectra(self):
        return self._spectra

    def setSpectra(self, spectra):
        self._spectra.clear()
        for key, spectrum in spectra.items():
            self.addToSpectra(spectrum, key)

    def addToSpectra(self, spectrum, key=None):
        if key is None:
            key = str(uuid.uuid4())
        spectrum.role = key           # the keyed-dict key IS spectrum.role
        self._spectra[key] = spectrum

    def getInputs(self):
        return self._inputs

    def setInputs(self, inputs):
        self._inputs = inputs

    def addToInputs(self, sourceSpectraContainer):
        self._inputs.append(sourceSpectraContainer)

    def getProducedBy(self):
        return self.producedBy

    def setProducedBy(self, producedBy):
        self.producedBy = producedBy
