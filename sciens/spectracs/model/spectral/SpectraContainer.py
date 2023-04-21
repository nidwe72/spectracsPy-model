from __future__ import annotations

import uuid
from typing import List, Dict


from spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep
from spectracs.model.spectral.Spectrum import Spectrum

class SpectraContainer:

    __spectra: Dict[str,Spectrum]=None
    __spectraContainers: Dict[str,SpectraContainer]=None
    __sourceSpectraContainer:SpectraContainer=None
    __workflowStep:SpectralWorkflowStep=None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__spectra= {}
        self.__spectraContainers = {}
        self.__sourceSpectraContainer=None
        self.__workflowStep=None

    def __init__(self):
        self.spectraBySampleTypes = {}

    def getSpectra(self)-> Dict[str,Spectrum]:
        result = self.__spectra
        return result

    def setSpectra(self, spectra: Dict[str,Spectrum]) :
        self.__spectra = spectra

    def addToSpectra(self, spectrum: Spectrum,key:str=None):
        if key is None:
            key=uuid.uuid4()
        self.__spectra[key]=spectrum

    def getSourceSpectraContainer(self):
        result = self.__sourceSpectraContainer
        return result

    def setSourceSpectraContainer(self, sourceSpectraContainer:SpectraContainer):
        self.__sourceSpectraContainer=sourceSpectraContainer

    def getWorkflowStep(self):
        result = self.__workflowStep
        return result

    def setWorkflowStep(self, workflowStep:SpectralWorkflowStep):
        self.__workflowStep=workflowStep
