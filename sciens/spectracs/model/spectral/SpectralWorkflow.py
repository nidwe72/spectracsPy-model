from typing import Dict

from sciens.spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
from sciens.spectracs.model.spectral.SpectralWorkflowPhaseType import SpectralWorkflowPhaseType
from sciens.spectracs.model.spectral.workflow.phase.acquireView.AcquireViewSpectralWorkflowPhase import \
    AcquireViewSpectralWorkflowPhase


class SpectralWorkflow:
    currentPhase: SpectralWorkflowPhase = None
    __phases: Dict[str, SpectralWorkflowPhase] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__phases = {}

    def getPhases(self):
        return self.__phases

    def setPhases(self, phases):
        self.__phases = phases

    def addToPhases(self, phase: SpectralWorkflowPhase):
        self.__phases[phase.getType()] = phase
        phase.setWorkflow(self)

    def getPhase(self, spectralWorkflowPhaseType: str):
        result = self.__phases.get(spectralWorkflowPhaseType)
        return result

    def getAcquireViewPhase(self) -> AcquireViewSpectralWorkflowPhase:
        result = self.getPhase(SpectralWorkflowPhaseType.ACQUIREMENT_VIEW)
        return result
