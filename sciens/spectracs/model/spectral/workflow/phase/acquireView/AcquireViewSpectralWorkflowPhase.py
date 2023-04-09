from typing import List

from spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
from spectracs.model.spectral.SpectralWorkflowPhaseType import SpectralWorkflowPhaseType
from spectracs.model.spectral.SpectrumSampleType import SpectrumSampleType


class AcquireViewSpectralWorkflowPhase(SpectralWorkflowPhase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setType(SpectralWorkflowPhaseType.ACQUIRE_VIEW)


    def getSpectralSampleTypes(self)->List[str]:
        result=[]
        result.append(SpectrumSampleType.SAMPLE)
        result.append(SpectrumSampleType.REFERENCE)
        return result