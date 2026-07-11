from abc import ABC, abstractmethod

from sciens.spectracs.logic.lims.dto.LimsHealth import LimsHealth
from sciens.spectracs.logic.lims.dto.LimsSampleRef import LimsSampleRef
from sciens.spectracs.logic.lims.dto.LimsSubmission import LimsSubmission


class LimsGateway(ABC):
    """The LIMS abstraction seam. One adapter per LIMS product implements this; everything upstream
    (plugin, server assembly) stays LIMS-agnostic. Swapping/adding a LIMS = write one adapter + register
    it with `LimsGatewayFactory`. See SPEC_lims_integration.md §4.

    There is no cross-LIMS library (SiLA 2 / AnIML / HL7 are instrument/data-level, not a registration
    API), so this thin seam is ours.
    """

    @abstractmethod
    def checkConnection(self) -> LimsHealth:
        """Is the LIMS reachable and are the credentials accepted (no side effects)."""

    @abstractmethod
    def submit(self, submission: LimsSubmission) -> LimsSampleRef:
        """Create the sample (ensuring/creating any prerequisite objects idempotently) and attach the
        report. Returns the created sample ref. Raises `LimsError` on failure."""
