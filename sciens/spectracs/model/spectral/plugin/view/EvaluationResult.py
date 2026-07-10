import json
import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import reconstructor

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.spectral.plugin.view.ViewModelFactory import ViewModelFactory


class EvaluationResult(DbBaseEntity, DbBaseEntityMixin):
    # Runtime object AND DB row (Option A). An ordered list of Qt-free view-models; the list is held in
    # memory (`items`) and persists as the `resultJson` TEXT column via toJson()/fromJson().

    stepId = Column(String, ForeignKey('spectral_workflow_step.id'))
    resultJson = Column(Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        self.__initTransient()

    @reconstructor
    def __initTransient(self):
        self._items = None

    def addItem(self, item):
        self.getItems().append(item)
        return self

    def getItems(self):
        if getattr(self, '_items', None) is None:
            self._items = self.__fromJson(self.resultJson)
        return self._items

    # --- serialization (SPEC_bench_pdf_export.md §5, D2) — delegates to the generic per-view-model protocol.
    # EvaluationResult no longer knows the view-model types: each item serializes itself (faithful by
    # construction — traces/bands/markers, capture descriptors, and metric style all round-trip now), and the
    # ViewModelFactory reconstructs from the "type" tag. Fixes both the report JSON and persisted-run reload
    # that previously dropped those fields. Unknown-type entries are skipped defensively. ---
    def toJson(self):
        return [item.toJson() for item in self.getItems() if hasattr(item, "toJson")]

    def syncToColumn(self):
        self.resultJson = json.dumps(self.toJson())

    def __fromJson(self, obj):
        if obj is None:
            return []
        if isinstance(obj, str):
            obj = json.loads(obj)
        items = []
        for entry in obj:
            view = ViewModelFactory.fromJson(entry)
            if view is not None:
                items.append(view)
        return items
