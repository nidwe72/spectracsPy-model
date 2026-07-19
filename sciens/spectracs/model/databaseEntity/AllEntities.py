"""Import EVERY database entity so both metadatas (DbBaseEntity for the app DB, ServerDbBaseEntity for the
server DB) are fully populated. Alembic's env.py imports this before reading `target_metadata`, and the
boot-time DatabaseInitializer imports it before create_all — otherwise a table whose module happens not to be
imported yet is invisible to the migration/create step (SPEC_schema_migrations.md §3.2).

Side-effect-only module: importing each entity registers its Table on the shared metadata.

COMPLETENESS IS ENFORCED, not merely requested: `spectracsPy/tests/test_all_entities_complete.py` walks the
model tree and fails (naming the table) if any DbBaseEntity/ServerDbBaseEntity subclass is missing from this list
(SPEC_schema_migrations.md §8). Add a new entity here AND the test stays green — forget, and it goes red."""

# --- app DB (DbBaseEntity) ---
from sciens.spectracs.model.databaseEntity.application import ApplicationConfig  # noqa: F401
from sciens.spectracs.model.databaseEntity.application import ApplicationConfigToSpectrometerProfile  # noqa: F401
# The model.spectral workflow graph — also DbBaseEntity / app-DB tables (SPEC_schema_migrations.md §8).
from sciens.spectracs.model.spectral import SpectralWorkflow  # noqa: F401
from sciens.spectracs.model.spectral import SpectralWorkflowPhase  # noqa: F401
from sciens.spectracs.model.spectral import SpectralWorkflowStep  # noqa: F401
from sciens.spectracs.model.spectral import SpectraContainer  # noqa: F401
from sciens.spectracs.model.spectral import Spectrum  # noqa: F401
from sciens.spectracs.model.spectral import SpectralWorkflowMetadata  # noqa: F401
from sciens.spectracs.model.spectral.plugin.view import EvaluationResult  # noqa: F401

# --- server DB (ServerDbBaseEntity) ---
from sciens.spectracs.model.databaseEntity.application.payment import Transaction  # noqa: F401
from sciens.spectracs.model.databaseEntity.application.plugin import DbPlugin  # noqa: F401
from sciens.spectracs.model.databaseEntity.application.user import AppUser  # noqa: F401
from sciens.spectracs.model.databaseEntity.application.user import AppUserRole  # noqa: F401
from sciens.spectracs.model.databaseEntity.application.user import AppUserToAppUserRole  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device.calibration import SpectrometerCalibrationProfile  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectralLineMasterData  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectralLine  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerProfile  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import Spectrometer  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerSensorChip  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerSensor  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerSetup  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerStyle  # noqa: F401
from sciens.spectracs.model.databaseEntity.spectral.device import SpectrometerVendor  # noqa: F401
