class SpectralWorkflowPhase:

    __type:str=None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getType(self):
        return self.__type

    def setType(self, phaseType):
        self.__type=phaseType

