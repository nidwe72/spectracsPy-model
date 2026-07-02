import uuid

try:
    from sciens.spectracs.model.spectral.SpectralWorkflowPhase import SpectralWorkflowPhase
except ImportError:
    # Circular import at load time — SpectralWorkflowPhase is only used as a type hint here, so fall back
    # to the partially-loaded module if present, else None (avoids a KeyError when Step is imported first).
    import sys
    __phaseModule = sys.modules.get(__package__ + '.SpectralWorkflowPhase')
    SpectralWorkflowPhase = getattr(__phaseModule, 'SpectralWorkflowPhase', None)


class SpectralWorkflowStep:
    __phase: SpectralWorkflowPhase = None
    __id: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__id = uuid.uuid4()
        # §9.3 carrier fields (SPEC_pumpkin_integration.md B.4). Durable ones stay data-only; view/widget
        # are transient/host-built (kept untyped so the model repo pulls in no Qt).
        self.__container = None
        self.__evaluationResult = None
        self.__view = None
        self.__widget = None
        self.__persist = False
        self.__role = None
        self.__label = None
        self.__frames = None
        self.__mandatory = False

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

    def getContainer(self):
        return self.__container

    def setContainer(self, container):
        self.__container = container

    def getEvaluationResult(self):
        return self.__evaluationResult

    def setEvaluationResult(self, evaluationResult):
        self.__evaluationResult = evaluationResult

    def getView(self):
        return self.__view

    def setView(self, view):
        self.__view = view

    def getWidget(self):
        return self.__widget

    def setWidget(self, widget):
        self.__widget = widget

    def getPersist(self) -> bool:
        return self.__persist

    def setPersist(self, persist: bool):
        self.__persist = persist

    def getRole(self):
        return self.__role

    def setRole(self, role):
        self.__role = role

    def getLabel(self):
        return self.__label

    def setLabel(self, label):
        self.__label = label

    def getFrames(self):
        return self.__frames

    def setFrames(self, frames):
        self.__frames = frames

    def getMandatory(self) -> bool:
        return self.__mandatory

    def setMandatory(self, mandatory: bool):
        self.__mandatory = mandatory
