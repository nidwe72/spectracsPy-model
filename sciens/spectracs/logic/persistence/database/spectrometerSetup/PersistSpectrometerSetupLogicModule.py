from typing import Optional

from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSetup import SpectrometerSetup
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerProfile import SpectrometerProfile
from sciens.spectracs.model.databaseEntity.spectral.device.calibration.SpectrometerCalibrationProfile import \
    SpectrometerCalibrationProfile


class PersistSpectrometerSetupLogicModule:
    # Server-side persistence for the serial-keyed instrument binding.
    # SPEC_connection_and_calibration_ux.md §3 / §9.

    def saveSpectrometerSetup(self, spectrometerSetup: SpectrometerSetup):
        session = server_session_factory()
        session.add(spectrometerSetup)
        session.commit()

    def resolveBySerial(self, serial: str) -> Optional[SpectrometerSetup]:
        # Walk the serial (which lives on SpectrometerProfile) up to its SpectrometerSetup.
        # This is the core of the resolve-by-serial RPC (A3).
        session = server_session_factory()
        return session.query(SpectrometerSetup) \
            .join(SpectrometerProfile, SpectrometerSetup.spectrometerProfileId == SpectrometerProfile.id) \
            .filter(SpectrometerProfile.serial == serial).first()

    def getOrCreateInstrument(self, serial: str, spectrometerId: str, pluginId: str) -> SpectrometerSetup:
        # Idempotent on serial: create the calibration + profile + setup graph if absent. The calibration
        # starts EMPTY (ROI/coeffs filled later by the master authoring GUI, Phase B). FK by id-string only,
        # so no cross-session attach of the passed spectrometer/plugin.
        existing = self.resolveBySerial(serial)
        if existing is not None:
            return existing

        session = server_session_factory()
        calibration = SpectrometerCalibrationProfile()

        profile = SpectrometerProfile()
        profile.serial = serial
        profile.spectrometerId = spectrometerId
        profile.spectrometerCalibrationProfile = calibration

        setup = SpectrometerSetup()
        setup.spectrometerProfile = profile
        setup.pluginId = pluginId

        session.add(calibration)
        session.add(profile)
        session.add(setup)
        session.commit()
        return setup
