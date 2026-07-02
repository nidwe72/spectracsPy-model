import json
import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import reconstructor

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.spectral.SpectrumSampleType import SpectrumSampleType


class Spectrum(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (SPEC_workflow_persistence.md, Option A). The {nm: value} map lives in memory
    # as the `valuesByNanometers` property and persists in the `valuesJson` TEXT column; toJson()/fromJson()
    # own the float-key cast (str out / float in). The ~N-frame capture burst + pixel colours stay transient
    # (NOT mapped). `role` is the bag key within the container (attribute_keyed_dict('role')).

    containerId = Column(String, ForeignKey('spectra_container.id'))
    role = Column(String)
    sampleType = Column(String)
    valuesJson = Column(Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.sampleType is None:
            self.sampleType = SpectrumSampleType.SAMPLE.value
        self.__initTransient()

    @reconstructor
    def __initTransient(self):
        self._values = None
        self._capturedValuesByNanometers = []
        self._colorsByPixelIndices = None

    # --- {nm: value} map: in-memory property backed by valuesJson ---
    @property
    def valuesByNanometers(self):
        if getattr(self, '_values', None) is None:
            self._values = self.__parse(self.valuesJson)
        return self._values

    @valuesByNanometers.setter
    def valuesByNanometers(self, values):
        self._values = values

    def setValuesByNanometers(self, values):
        self.valuesByNanometers = values

    # --- serialization (P2) — the single tested home for the float-key cast ---
    def toJson(self):
        return {str(nm): value for nm, value in self.valuesByNanometers.items()}

    def fromJson(self, obj):
        self.valuesByNanometers = self.__parse(obj)
        return self

    def syncToColumn(self):
        # called by the persist util before commit so the column reflects the in-memory map
        self.valuesJson = json.dumps(self.toJson())

    def __parse(self, obj):
        if obj is None:
            return {}
        if isinstance(obj, str):
            obj = json.loads(obj)
        return {float(k): v for k, v in obj.items()}

    def getSampleType(self):
        return self.sampleType

    def setSampleType(self, sampleType):
        self.sampleType = sampleType

    def getCapturedValuesByNanometers(self):
        return self._capturedValuesByNanometers

    def addToCapturedValuesByNanometers(self, capturedValuesByNanometers):
        self._capturedValuesByNanometers.append(capturedValuesByNanometers)

    def getColorsByPixelIndices(self):
        return self._colorsByPixelIndices

    def setColorsByPixelIndices(self, colorsByPixelIndices):
        self._colorsByPixelIndices = colorsByPixelIndices
