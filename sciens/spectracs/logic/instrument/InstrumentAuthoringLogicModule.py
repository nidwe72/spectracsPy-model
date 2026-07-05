import json

from sciens.spectracs.logic.model.util.SpectrometerUtil import SpectrometerUtil
from sciens.spectracs.logic.spectral.util.SpectralLineMasterDataUtil import SpectralLineMasterDataUtil
from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.application.plugin.DbPlugin import DbPlugin
from sciens.spectracs.model.databaseEntity.spectral.device.Spectrometer import Spectrometer
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensor import SpectrometerSensor
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerProfile import SpectrometerProfile
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSetup import SpectrometerSetup
from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLine import SpectralLine
from sciens.spectracs.model.databaseEntity.spectral.device.SpectralLineMasterData import SpectralLineMasterData
from sciens.spectracs.model.databaseEntity.spectral.device.calibration.SpectrometerCalibrationProfile import \
    SpectrometerCalibrationProfile


class InstrumentAuthoringLogicModule:
    """MASTER-side authoring persistence (SPEC_connection_and_calibration_ux.md §4.1).

    Runs on the server. The master client saves via RPC so the serial-object lands on the authoritative
    server DB (where end-user registration/login resolve it). Upserts are keyed on the SERIAL.
    """

    __CAL_FIELDS = ("regionOfInterestX1", "regionOfInterestY1", "regionOfInterestX2", "regionOfInterestY2",
                    "interpolationCoefficientA", "interpolationCoefficientB",
                    "interpolationCoefficientC", "interpolationCoefficientD")

    def __findSpectrometerByDevice(self, session, deviceCodeName):
        spectrometer = session.query(Spectrometer).join(
            SpectrometerSensor, Spectrometer.spectrometerSensorId == SpectrometerSensor.id).filter(
            SpectrometerSensor.codeName == deviceCodeName).first()
        if spectrometer is None:
            SpectrometerUtil().getSpectrometers()  # seed the catalog if empty, then retry
            spectrometer = session.query(Spectrometer).join(
                SpectrometerSensor, Spectrometer.spectrometerSensorId == SpectrometerSensor.id).filter(
                SpectrometerSensor.codeName == deviceCodeName).first()
        return spectrometer

    def saveProfile(self, serial: str, deviceCodeName: str, calibration: dict) -> dict:
        if not serial:
            return {"ok": False, "message": "serial is required"}
        session = server_session_factory()

        spectrometer = self.__findSpectrometerByDevice(session, deviceCodeName)
        if spectrometer is None:
            return {"ok": False, "message": "unknown device '%s'" % deviceCodeName}

        profile = session.query(SpectrometerProfile).filter(SpectrometerProfile.serial == serial).first()
        if profile is None:
            profile = SpectrometerProfile()
            profile.serial = serial
            profile.spectrometerCalibrationProfile = SpectrometerCalibrationProfile()
        cal = profile.spectrometerCalibrationProfile
        if cal is None:
            cal = SpectrometerCalibrationProfile()
            profile.spectrometerCalibrationProfile = cal

        profile.spectrometerId = spectrometer.id
        if calibration:
            for field in self.__CAL_FIELDS:
                if field in calibration and calibration[field] is not None:
                    setattr(cal, field, calibration[field])
            self.__saveSpectralLines(session, cal, calibration.get("spectralLines"))
            spectrum = calibration.get("spectrum")
            if spectrum is not None:
                cal.calibrationSpectrumJson = json.dumps(spectrum)

        session.add(cal)
        session.add(profile)
        session.commit()
        return {"ok": True, "serial": serial, "profileId": profile.id}

    def __saveSpectralLines(self, session, cal, lines):
        # Round-trip the detected calibration lines (pixelIndex <-> master-data nanometer). Rebuild the
        # child rows from the DTO, linking each to the seeded SpectralLineMasterData by name (then nm).
        if lines is None:
            return
        masterDataByName = SpectralLineMasterDataUtil().getSpectralLineMasterDatasByNames()  # seed if empty
        rebuilt = []
        for entry in lines:
            pixelIndex = entry.get("pixelIndex")
            if pixelIndex is None:
                continue
            masterData = masterDataByName.get(entry.get("name")) if entry.get("name") else None
            if masterData is None and entry.get("nanometer") is not None:
                masterData = session.query(SpectralLineMasterData).filter(
                    SpectralLineMasterData.nanometer == entry.get("nanometer")).first()
            spectralLine = SpectralLine()
            spectralLine.pixelIndex = int(pixelIndex)
            if masterData is not None:
                spectralLine.spectralLineMasterDataId = masterData.id
            rebuilt.append(spectralLine)
        cal.spectralLines = rebuilt  # delete-orphan cascade drops any previous set

    def saveSetup(self, serial: str, pluginCodeRef: str) -> dict:
        session = server_session_factory()
        profile = session.query(SpectrometerProfile).filter(SpectrometerProfile.serial == serial).first()
        if profile is None:
            return {"ok": False, "message": "no profile for serial '%s' — save the profile first" % serial}
        plugin = session.query(DbPlugin).filter(DbPlugin.codeRef == pluginCodeRef).first()
        if plugin is None:
            return {"ok": False, "message": "unknown plugin '%s'" % pluginCodeRef}

        setup = session.query(SpectrometerSetup).filter(
            SpectrometerSetup.spectrometerProfileId == profile.id).first()
        if setup is None:
            setup = SpectrometerSetup()
            setup.spectrometerProfileId = profile.id
        setup.pluginId = plugin.id
        session.add(setup)
        session.commit()
        return {"ok": True, "serial": serial, "setupId": setup.id}

    def listProfiles(self) -> list:
        session = server_session_factory()
        result = []
        for p in session.query(SpectrometerProfile).all():
            device = None
            if p.spectrometer is not None and p.spectrometer.spectrometerSensor is not None:
                device = p.spectrometer.spectrometerSensor.codeName
            result.append({"id": p.id, "serial": p.serial, "deviceCodeName": device})
        return result

    def listSetups(self) -> list:
        session = server_session_factory()
        result = []
        for s in session.query(SpectrometerSetup).all():
            serial = s.spectrometerProfile.serial if s.spectrometerProfile is not None else None
            pluginCodeRef = s.plugin.codeRef if s.plugin is not None else None
            result.append({"id": s.id, "serial": serial, "pluginCodeRef": pluginCodeRef})
        return result
