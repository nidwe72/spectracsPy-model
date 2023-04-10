from typing import List

from spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep
from spectracs.model.spectral.SpectrumSampleType import SpectrumSampleType


class AcquireViewSpectralWorkflowStep(SpectralWorkflowStep):

    def getSpectralSampleTypes(self)->List[str]:
        result=[]
        result.append(SpectrumSampleType.SAMPLE)
        result.append(SpectrumSampleType.REFERENCE)
        return result