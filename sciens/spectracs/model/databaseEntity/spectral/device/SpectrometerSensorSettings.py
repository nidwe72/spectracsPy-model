class SpectrometerSensorSettings:
    """Per-camera capture parameters, judged empirically per light source and seeded per camera in
    SpectrometerSensorUtil (SPEC_real_camera_capture.md §4/§9.3). NOT user-tuned per DB row — the device
    is DIY with a small, known camera set. Two exposure regimes per camera, because there are two light
    sources doing two different jobs:

      calibrationExposure — CFL line source (wavelength calibration): the highest value that keeps the
                            brightest mercury line (green ~546 nm) UNCLIPPED, so the calibration lines
                            centroid cleanly and the green doublet is as resolved as the optics allow.
      measurementExposure — LED-array broadband source (the reference + sample capture during an actual
                            measurement): a different, brighter-source regime — its own value(s), TBD.

    Values are V4L2 manual-exposure units (the backend sets AUTO_EXPOSURE=1 = manual, then this value).
    None => fall back to the legacy default (150 on Linux)."""

    def __init__(self, calibrationExposure: int = None, measurementExposure: int = None):
        self.calibrationExposure = calibrationExposure
        self.measurementExposure = measurementExposure
