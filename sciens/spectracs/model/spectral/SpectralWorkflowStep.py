import uuid

try:
    from sciens.spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
except ImportError:
    import sys
    SpectralWorkflowPhase = sys.modules[__package__ + '.SpectralWorkflowPhase']


class SpectralWorkflowStep:
    __phase: SpectralWorkflowPhase = None
    __id: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__id = uuid.uuid4()

    def getPhase(self) -> SpectralWorkflowPhase:
        result = self.__phase
        return result

    def setPhase(self, phase: SpectralWorkflowPhase):
        self.__phase = phase

    def getId(self) -> str:
        result = self.__id
        return result

    def setId(self, id: str):
        self.__id=id
