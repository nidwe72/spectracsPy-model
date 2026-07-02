from __future__ import annotations

import uuid
from typing import Dict, List

from sciens.spectracs.model.spectral.SpectralWorkflowStep import SpectralWorkflowStep
from sciens.spectracs.model.spectral.Spectrum import Spectrum


class SpectraContainer:
    # One stage of a run: named bags of spectra that remember their lineage
    # (SPECTRAL_WORKFLOW_CONCEPT.md 9.2 / SPEC_pumpkin_integration.md A.0).
    #   spectra    : { role -> Spectrum }        the data
    #   inputs     : [ SpectraContainer ]        SOURCE / provenance (a LIST — absorption needs two)
    #   producedBy : SpectralWorkflowStep        OWNER (the step that produced this container)

    __spectra: Dict[str, Spectrum] = None
    __inputs: List[SpectraContainer] = None
    __producedBy: SpectralWorkflowStep = None

    def __getSpectra(self) -> Dict[str, Spectrum]:
        # Lazy init (no __init__: this is used by Singleton-flavoured callers where __init__ re-runs).
        if self.__spectra is None:
            self.__spectra = {}
        return self.__spectra

    def __getInputs(self) -> List[SpectraContainer]:
        if self.__inputs is None:
            self.__inputs = []
        return self.__inputs

    def getSpectra(self) -> Dict[str, Spectrum]:
        return self.__getSpectra()

    def setSpectra(self, spectra: Dict[str, Spectrum]):
        self.__spectra = spectra

    def addToSpectra(self, spectrum: Spectrum, key: str = None):
        if key is None:
            key = str(uuid.uuid4())
        self.__getSpectra()[key] = spectrum

    def getInputs(self) -> List[SpectraContainer]:
        return self.__getInputs()

    def setInputs(self, inputs: List[SpectraContainer]):
        self.__inputs = inputs

    def addToInputs(self, sourceSpectraContainer: SpectraContainer):
        self.__getInputs().append(sourceSpectraContainer)

    def getProducedBy(self) -> SpectralWorkflowStep:
        return self.__producedBy

    def setProducedBy(self, producedBy: SpectralWorkflowStep):
        self.__producedBy = producedBy
