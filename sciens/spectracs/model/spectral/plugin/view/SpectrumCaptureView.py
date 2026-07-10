from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class SpectrumCaptureView(ReportableView):
    # SPEC_plugin_driven_convergence.md §3 (P2) — the captured raster the spectrum is extracted from. A
    # plugin-declared SHELL: the plugin sets the caption + the crop/overlay flags, and its very presence means
    # "show this frame". The HOST fills `.image` after capture (it applies the crop / ROI overlay and injects
    # the pixels the plugin cannot know in advance). Passive → rendered through the visitor like any other
    # view-model; only `.image` is host-populated before dispatch.
    #
    # M2 (SPEC_bench_pdf_export.md §5b): the pixels are NOT serialized into the report JSON (no base64 bloat) —
    # the descriptor carries an `attachmentName`, and the host embeds the image as that named PDF attachment
    # (extractable on command). `reportImage` is the Qt-free rendition (a PIL image) the host derives from
    # `.image` so the matplotlib report renderer stays Qt-free.

    def __init__(self, caption=None, cropped=False, roiOverlay=False):
        self.caption = caption
        self.cropped = cropped        # crop to the ROI (True) vs the full frame (False)
        self.roiOverlay = roiOverlay  # paint the ROI rectangle on the frame
        self.image = None             # host-set: the raster (masked / cropped per the flags above; a QImage)
        self.attachmentName = None    # host-set: the /EmbeddedFiles name this capture is attached under (§5b)
        self.reportImage = None       # host-set: Qt-free PIL rendition for the matplotlib report renderer

    # --- serialization (SPEC_bench_pdf_export.md §5/§5b, D2): descriptor + attachmentName only, NEVER pixels ---
    def toJson(self):
        return {"type": "capture", "caption": self.caption, "cropped": self.cropped,
                "roiOverlay": self.roiOverlay, "attachmentName": self.attachmentName,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(entry.get("caption"), entry.get("cropped", False), entry.get("roiOverlay", False))
        view.attachmentName = entry.get("attachmentName")
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
