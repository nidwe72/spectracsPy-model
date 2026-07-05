from sciens.spectracs.logic.persistence.database.spectrometerSetup.PersistSpectrometerSetupLogicModule import \
    PersistSpectrometerSetupLogicModule


class InstrumentLogicModule:
    """Resolve the instrument bundle for a serial (SPEC_connection_and_calibration_ux.md §4.3).

    serial -> SpectrometerProfile (device + calibration) -> its SpectrometerSetup -> plugin.
    Returns a plain, Pyro-serializable dict; the client caches it into CurrentUserSession at login.
    """

    def resolveBundle(self, serial: str) -> dict:
        if serial is None:
            return {"ok": False, "serial": None, "message": "no serial"}

        setup = PersistSpectrometerSetupLogicModule().resolveBySerial(serial)
        if setup is None:
            # End-user-facing wording reuses the factory-calibration message (spec §4.2 E2).
            return {"ok": False, "serial": serial,
                    "message": "Your spectrometer has been calibrated in the factory, but the "
                               "calibration could not be downloaded (unknown serial)."}

        profile = setup.spectrometerProfile
        spectrometer = profile.spectrometer if profile is not None else None
        sensor = spectrometer.spectrometerSensor if spectrometer is not None else None
        deviceCodeName = sensor.codeName if sensor is not None else None
        pluginCodeRef = setup.plugin.codeRef if setup.plugin is not None else None

        calibration = None
        cal = profile.spectrometerCalibrationProfile if profile is not None else None
        if cal is not None and cal.interpolationCoefficientA is not None:
            calibration = {
                "regionOfInterestX1": cal.regionOfInterestX1,
                "regionOfInterestY1": cal.regionOfInterestY1,
                "regionOfInterestX2": cal.regionOfInterestX2,
                "regionOfInterestY2": cal.regionOfInterestY2,
                "interpolationCoefficientA": cal.interpolationCoefficientA,
                "interpolationCoefficientB": cal.interpolationCoefficientB,
                "interpolationCoefficientC": cal.interpolationCoefficientC,
                "interpolationCoefficientD": cal.interpolationCoefficientD,
            }

        return {"ok": True, "serial": serial, "deviceCodeName": deviceCodeName,
                "pluginCodeRef": pluginCodeRef, "calibration": calibration, "message": None}
