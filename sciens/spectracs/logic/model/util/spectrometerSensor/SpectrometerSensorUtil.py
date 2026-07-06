from typing import Dict

from sciens.base.Singleton import Singleton
from sciens.spectracs.logic.model.util.SpectrometerSensorChipUtil import SpectrometerSensorChipUtil
from sciens.spectracs.logic.persistence.database.spectrometerSensor.PersistSpectrometerSensorLogicModule import \
    PersistSpectrometerSensorLogicModule
from sciens.spectracs.logic.persistence.database.spectrometerSensor.PersistenceParametersGetSpectrometerSensors import \
    PersistenceParametersGetSpectrometerSensors
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensor import SpectrometerSensor
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorCodeName import SpectrometerSensorCodeName
from sciens.spectracs.model.databaseEntity.spectral.device.SpectrometerSensorSettings import SpectrometerSensorSettings


class SpectrometerSensorUtil(Singleton):

    # Good per-camera capture exposures, judged empirically against the light source and hard-coded HERE
    # (where the cameras are seeded), keyed by hardwareId = vendorId_modelId (SPEC_real_camera_capture.md
    # §4/§9.3, KB_spectroscopy_physics.md §7). calibrationExposure verified on the CFL line source:
    # 78 is the highest value that keeps the ELP's green ~546 nm line unclipped (150 clipped blue+green
    # and merged the whole red cluster). measurementExposure (LED array, ref+sample) is a separate regime,
    # still TBD. None => backend legacy default (150 Linux).
    __CAPTURE_SETTINGS_BY_HARDWARE_ID = {
        '32e4_8830': SpectrometerSensorSettings(calibrationExposure=78, measurementExposure=None),   # ELP
        '0c45_6366': SpectrometerSensorSettings(calibrationExposure=None, measurementExposure=None),  # Microdia TBD
    }

    def getSensorSettings(self, spectrometerSensor: SpectrometerSensor) -> SpectrometerSensorSettings:
        if spectrometerSensor is None:
            return SpectrometerSensorSettings()
        return self.__CAPTURE_SETTINGS_BY_HARDWARE_ID.get(
            self.getHardwareId(spectrometerSensor), SpectrometerSensorSettings())

    def getPersistedSpectrometerSensors(self) -> Dict[int, SpectrometerSensor]:
        module = PersistSpectrometerSensorLogicModule()
        parameters = PersistenceParametersGetSpectrometerSensors()
        result=module.getSpectrometerSensors(parameters)
        return result

    def getSpectrometerSensors(self) -> Dict[str, SpectrometerSensor]:
        transientEntities = {}

        sensorChips = SpectrometerSensorChipUtil().getSpectrometerSensorChips()

        virtualDevice = SpectrometerSensor()
        virtualDevice.codeName = SpectrometerSensorCodeName.VIRTUAX
        virtualDevice.isVirtual=True
        virtualDevice.description = "virtual spectrometer"
        virtualDevice.vendorId = "0c99"
        virtualDevice.vendorName = "Spectracs"
        virtualDevice.sellerName = "Spectracs"
        virtualDevice.modelId = "9999"
        virtualDevice.spectrometerSensorChip=sensorChips['Spectracs_9999']
        virtualDevice.spectrometerSensorChipId = sensorChips['Spectracs_9999'].id
        transientEntities[virtualDevice.codeName] = virtualDevice

        microdiaDevice = SpectrometerSensor()
        microdiaDevice.codeName = SpectrometerSensorCodeName.AUTOMAT
        microdiaDevice.isVirtual = False
        microdiaDevice.description = "Thunder optics"
        microdiaDevice.vendorId = "0c45"
        microdiaDevice.vendorName = "Microdia"
        microdiaDevice.sellerName = "ThunderOptics"
        microdiaDevice.modelId = "6366"
        microdiaDevice.spectrometerSensorChip=sensorChips['Sonix_6366']
        microdiaDevice.spectrometerSensorChipId = sensorChips['Sonix_6366'].id
        transientEntities[microdiaDevice.codeName] = microdiaDevice

        elp4KDevice = SpectrometerSensor()
        elp4KDevice.codeName = SpectrometerSensorCodeName.EXAKTA
        elp4KDevice.isVirtual = False
        elp4KDevice.description = "ELP "
        elp4KDevice.vendorId = "32e4"
        elp4KDevice.vendorName = "ELP"
        elp4KDevice.modelId = "8830"
        elp4KDevice.sellerName = "ELP"
        elp4KDevice.spectrometerSensorChip=sensorChips['Sony_IMX1234']
        elp4KDevice.spectrometerSensorChipId = sensorChips['Sony_IMX1234'].id
        transientEntities[elp4KDevice.codeName]=elp4KDevice

        persistLogicModule = PersistSpectrometerSensorLogicModule()

        # todo:performance
        # do not load always load all entities
        persistenceParameters = PersistenceParametersGetSpectrometerSensors()

        entitiesByIds = persistLogicModule.getSpectrometerSensors(
            persistenceParameters)

        entitiesByCodeNames = self.getEntitiesByCodeNames(entitiesByIds);

        result = {}

        for entityCodeName, entity in transientEntities.items():
            persistedEntity = entitiesByCodeNames.get(entityCodeName)

            if persistedEntity is None:
                persistLogicModule.saveSpectrometerSensor(entity)
                result[entity.codeName ] = entity
                continue
            else:
                result[entity.codeName] = persistedEntity

        return result

    def getEntitiesByCodeNames(self, entitiesByIds:Dict[str, SpectrometerSensor]):
        result={}
        for entityId, entity in entitiesByIds.items():
            result[entity.codeName]=entity
        return result


    def getHardwareId(self, spectrometerSensor: SpectrometerSensor):
        result = spectrometerSensor.vendorId + '_' + spectrometerSensor.modelId
        return result

    def getSensorByCodeName(self, spectrometerSensorCodenName) -> SpectrometerSensor:
        spectrometerSensors = self.getSpectrometerSensors()
        result = spectrometerSensors.get(spectrometerSensorCodenName)
        return result

    def getSensorMarkup(self, spectrometerSensor: SpectrometerSensor):
        html = \
            '''            
            <style type="text/css">                
                table {
                    color: gray;
                    border: 1px solid red;
                    border-width: 0px;
                    border-collapse: collapse;                    
                }               
            </style>            
            <body width=100% border=1>
            <table width=100% border=1>
            <tr>
                <td colspan="4" style="font-weight:bold;text-align: center;background-color:#404040;padding:5px;">%codeName%</td>
            </tr>
            <tr>
                <td width=25%>Code name</td>
                <td width=25%>Vendor</td>
                <td width=25%>Vendor id</td>
                <td width=24.8%>Model id</td>
                               
            </tr>                        
            <tr>
                <td width=25%>%codeName%</td>
                <td width=25%>%vendorName%</td>
                <td width=25%>%vendorId%</td>
                <td width=24.8%>%modelId%</td>                                
            </tr>
            </table>
            
            
            <table width=100% border=1>
            <tr>
                <td width=25% style="font-weight:bold;text-align: center;background-color:#404040;padding:5px;">Sensor</td>
                <td width=19%>Vendor</td>
                <td width=18.5%>%sensorVendorName%</td>
                <td width=19%>Model id</td>
                <td width=18.3%>%sensorProductName%</td>                                
            </tr>                        
            </table>
            
            
            </body>
            '''

        html = html.replace('%vendorId%', spectrometerSensor.vendorId)
        html = html.replace('%vendorName%', spectrometerSensor.vendorName)
        html = html.replace('%modelId%', spectrometerSensor.modelId)
        html = html.replace('%codeName%', spectrometerSensor.codeName)
        html = html.replace('%sensorVendorName%', spectrometerSensor.spectrometerSensorChip.vendorName)
        html = html.replace('%sensorProductName%', spectrometerSensor.spectrometerSensorChip.productName)

        return html
