from typing import List, Dict

from spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
from spectracs.model.spectral.SpectralWorkflowPhaseType import SpectralWorkflowPhaseType
from spectracs.model.spectral.workflow.phase.setp.AcquireViewSpectralWorkflowStep import AcquireViewSpectralWorkflowStep


class AcquireViewSpectralWorkflowPhase(SpectralWorkflowPhase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setType(SpectralWorkflowPhaseType.ACQUIREMENT_VIEW)

    def getSteps(self)->Dict[str,AcquireViewSpectralWorkflowStep]:
        result = super().getSteps()
        return result
