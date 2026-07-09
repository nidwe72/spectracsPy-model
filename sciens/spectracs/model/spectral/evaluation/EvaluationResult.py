import json
import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import reconstructor

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntity, DbBaseEntityMixin
from sciens.spectracs.model.spectral.evaluation.ColorSwatchView import ColorSwatchView
from sciens.spectracs.model.spectral.evaluation.LabelView import LabelView
from sciens.spectracs.model.spectral.evaluation.MetricFieldView import MetricFieldView
from sciens.spectracs.model.spectral.evaluation.SpectrumPlotView import SpectrumPlotView
from sciens.spectracs.model.spectral.evaluation.VerdictView import VerdictView


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

    # --- serialization (P2) ---
    def toJson(self):
        result = []
        for item in self.getItems():
            if isinstance(item, ColorSwatchView):
                result.append({"type": "swatch", "rgb": list(item.rgb), "label": item.label})
            elif isinstance(item, VerdictView):
                result.append({"type": "verdict", "roastState": item.roastState,
                               "hueDegrees": item.hueDegrees})
            elif isinstance(item, MetricFieldView):
                result.append({"type": "metric", "label": item.label, "value": item.value,
                               "tooltip": item.tooltip})
            elif isinstance(item, LabelView):
                result.append({"type": "label", "text": item.text})
            elif isinstance(item, SpectrumPlotView):
                spectrum = item.spectrum
                result.append({"type": "plot", "title": item.title,
                               "values": spectrum.toJson() if spectrum is not None else {}})
        return result

    def syncToColumn(self):
        self.resultJson = json.dumps(self.toJson())

    def __fromJson(self, obj):
        if obj is None:
            return []
        if isinstance(obj, str):
            obj = json.loads(obj)
        items = []
        for entry in obj:
            kind = entry.get("type")
            if kind == "swatch":
                items.append(ColorSwatchView(tuple(entry["rgb"]), entry.get("label")))
            elif kind == "verdict":
                items.append(VerdictView(entry["roastState"], entry.get("hueDegrees")))
            elif kind == "metric":
                items.append(MetricFieldView(entry["label"], entry["value"], entry.get("tooltip")))
            elif kind == "label":
                items.append(LabelView(entry["text"]))
            elif kind == "plot":
                from sciens.spectracs.model.spectral.Spectrum import Spectrum
                items.append(SpectrumPlotView(Spectrum().fromJson(entry.get("values", {})),
                                              entry.get("title")))
        return items
