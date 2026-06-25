from sciens.spectracs.model.databaseEntity.DbBase import session_factory
from sciens.spectracs.model.databaseEntity.spectral.device.calibration.SpectrometerCalibrationProfile import \
    SpectrometerCalibrationProfile


class PersistSpectrometerCalibrationProfileLogicModule:

    def saveSpectrometerCalibrationProfile(self, spectrometerCalibrationProfile: SpectrometerCalibrationProfile):
        session = session_factory()

        # Track the profile and make sure it has an id before linking children.
        session.add(spectrometerCalibrationProfile)
        session.flush()

        # Explicitly link the current spectral lines to this profile so they are never persisted
        # orphaned (spectrometerCalibrationProfile_id = NULL), which is what made saved calibration
        # profiles appear empty after reload. delete-orphan on the relationship removes any lines
        # dropped from the collection (e.g. when re-running peak detection).
        for spectralLine in list(spectrometerCalibrationProfile.getSpectralLines() or []):
            spectralLine.spectrometerCalibrationProfile = spectrometerCalibrationProfile

        session.commit()
