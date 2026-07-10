from sciens.spectracs.model.spectral.plugin.view.ColorSwatchView import ColorSwatchView
from sciens.spectracs.model.spectral.plugin.view.LabelView import LabelView
from sciens.spectracs.model.spectral.plugin.view.MetricFieldView import MetricFieldView
from sciens.spectracs.model.spectral.plugin.view.SpectrumCaptureView import SpectrumCaptureView
from sciens.spectracs.model.spectral.plugin.view.SpectrumPlotView import SpectrumPlotView
from sciens.spectracs.model.spectral.plugin.view.VerdictView import VerdictView


class ViewModelFactory:
    # SPEC_bench_pdf_export.md §5 (D2) — the ONE place that maps a serialized view-model's "type" tag back to
    # its class. Each view-model owns its toJson()/fromJson(); this factory just routes reconstruction, so the
    # serialization stays faithful-by-construction (no central ladder that drifts lossy). Used by
    # EvaluationResult.fromJson and by any report-JSON reload.

    __BY_TYPE = {
        "label": LabelView,
        "metric": MetricFieldView,
        "swatch": ColorSwatchView,
        "verdict": VerdictView,
        "plot": SpectrumPlotView,
        "capture": SpectrumCaptureView,
    }

    @classmethod
    def fromJson(cls, entry):
        viewClass = cls.__BY_TYPE.get(entry.get("type"))
        if viewClass is None:
            return None
        return viewClass.fromJson(entry)
