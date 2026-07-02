from enum import Enum


class VirtualCaptureRole(str, Enum):
    # The three images a virtual spectrometer holds for a pumpkin run (SPEC_pumpkin_integration.md A.1).
    CALIBRATION = 'CALIBRATION'
    REFERENCE = 'REFERENCE'
    SAMPLE = 'SAMPLE'
