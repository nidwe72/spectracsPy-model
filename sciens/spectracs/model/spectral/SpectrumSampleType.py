
from enum import Enum

class SpectrumSampleType(str,Enum):
    REFERENCE='REFERENCE'
    SAMPLE='SAMPLE'
    DARK='DARK'
    BLANK='BLANK'
    UNSPECIFIED = 'UNSPECIFIED'

