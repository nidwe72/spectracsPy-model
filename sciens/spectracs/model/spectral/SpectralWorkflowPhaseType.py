from enum import Enum

class SpectralWorkflowPhaseType(str,Enum):

    # Legacy values — KEPT (still used by SpectralWorkflow.getAcquireViewPhase / SpectralJobViewModule);
    # superseded by the canonical 5-phase spine below, retire once the engine (Track C) lands.
    ACQUIREMENT_VIEW= 'ACQUIREMENT_VIEW'
    ACQUIREMENT = 'ACQUIREMENT'

    # Canonical 5-phase spine (SPEC_pumpkin_integration.md B.4 / concept §9.1).
    ACQUISITION = 'ACQUISITION'
    PROCESSING = 'PROCESSING'
    EVALUATION = 'EVALUATION'
    METADATA = 'METADATA'
    PUBLISHING = 'PUBLISHING'
