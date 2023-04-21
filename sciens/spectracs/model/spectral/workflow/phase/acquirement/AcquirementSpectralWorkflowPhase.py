from sciens.spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
from sciens.spectracs.model.spectral.SpectralWorkflowPhaseType import SpectralWorkflowPhaseType

class AcquirementSpectralWorkflowPhase(SpectralWorkflowPhase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setType(SpectralWorkflowPhaseType.ACQUIREMENT)



