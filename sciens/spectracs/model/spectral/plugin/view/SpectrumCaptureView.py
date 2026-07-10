class SpectrumCaptureView:
    # SPEC_plugin_driven_convergence.md §3 (P2) — the captured raster the spectrum is extracted from. A
    # plugin-declared SHELL: the plugin sets the caption + the crop/overlay flags, and its very presence means
    # "show this frame". The HOST fills `.image` after capture (it applies the crop / ROI overlay and injects
    # the pixels the plugin cannot know in advance). Passive → rendered through the visitor like any other
    # view-model; only `.image` is host-populated before dispatch.

    def __init__(self, caption=None, cropped=False, roiOverlay=False):
        self.caption = caption
        self.cropped = cropped        # crop to the ROI (True) vs the full frame (False)
        self.roiOverlay = roiOverlay  # paint the ROI rectangle on the frame
        self.image = None             # host-set: the raster (masked / cropped per the flags above)
