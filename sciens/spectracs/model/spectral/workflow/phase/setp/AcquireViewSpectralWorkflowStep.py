from typing import List

from sciens.spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep
from sciens.spectracs.model.spectral.SpectrumSampleType import SpectrumSampleType


class AcquireViewSpectralWorkflowStep(SpectralWorkflowStep):

    def getSpectralSampleTypes(self)->List[str]:
        result=[]
        result.append(SpectrumSampleType.SAMPLE)
        result.append(SpectrumSampleType.REFERENCE)
        return result