from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from typing import Dict
from spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep

try:
    from spectracs.model.spectral.SpectralWorkflow import SpectralWorkflow
except ImportError:
    import sys
    SpectralWorkflow = sys.modules[__package__ + '.SpectralWorkflow']


class SpectralWorkflowPhase:
    __type: str = None
    __workflow: SpectralWorkflow = None
    __steps:Dict[str,SpectralWorkflowStep]=None
    __id: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__id = uuid.uuid4()
        self.__type = None
        self.__workflow = None
        self.__steps = {}

    def getType(self):
        return self.__type

    def setType(self, phaseType):
        self.__type = phaseType

    def getWorkflow(self):
        return self.__workflow

    def setWorkflow(self, workflow):
        self.__workflow = workflow

    def getSteps(self):
        return self.__steps

    def setSteps(self, steps:Dict[str,SpectralWorkflowStep]):
        self.__steps = steps

    def addToSteps(self, step:SpectralWorkflowStep):
        self.__steps[step.getId()] = step

    def getId(self) -> str:
        result = self.__id
        return result

    def setId(self, id: str):
        self.__id

