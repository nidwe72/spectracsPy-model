from sciens.spectracs.logic.lims.LimsGateway import LimsGateway
from sciens.spectracs.logic.lims.dto.LimsHealth import LimsHealth
from sciens.spectracs.logic.lims.dto.LimsSampleRef import LimsSampleRef
from sciens.spectracs.logic.lims.dto.LimsSubmission import LimsSubmission


class MockLimsGateway(LimsGateway):
    """In-memory LIMS adapter for tests and offline dev — no network. Records every submission and
    returns a deterministic sample id built from the sample-type code (e.g. "OIL-0001"). Lets the whole
    upstream path (plugin -> RPC -> submission assembly) be exercised without a live LIMS.
    See SPEC_lims_integration.md §4 / L1.
    """

    def __init__(self, configKey: str = "MOCK"):
        self.configKey = configKey
        self.submissions = []           # every submission passed to submit(), in order
        self._counter = 0

    def checkConnection(self) -> LimsHealth:
        return LimsHealth(True, "mock LIMS ready")

    def submit(self, submission: LimsSubmission) -> LimsSampleRef:
        self.submissions.append(submission)
        self._counter += 1
        prefix = (submission.sampleType.code or "SMP").upper()
        sampleId = "%s-%04d" % (prefix, self._counter)
        return LimsSampleRef(sampleId, url=None)

    @property
    def lastSubmission(self):
        return self.submissions[-1] if self.submissions else None
