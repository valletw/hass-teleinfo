""" Teleinfo entities. """
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity
)
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_NAME,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfApparentPower
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR
)


class TeleinfoEntity(CoordinatorEntity, SensorEntity):
    """ Teleinfo entity. """

    _FIELD = "unknown"
    _DESC = "Unknown"
    _attr_should_poll = False

    def __init__(self, coordinator, uid: str, device: str):
        super().__init__(coordinator)
        self.entity_id = f"{SENSOR}.{DOMAIN}_{device.lower()}_{self._FIELD.lower()}"
        self._attr_unique_id = f"{uid}-{self._FIELD.lower()}"
        self._attr_name = self._DESC
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, uid)},
            ATTR_NAME: device,
            ATTR_MANUFACTURER: "EDF",
        }

    @staticmethod
    def _convert_data(_):
        """ Convert data to native value format. """
        return None

    @property
    def native_value(self):
        """ Get data from coordinator and convert it. """
        if self._FIELD in self.coordinator.data:
            return self._convert_data(self.coordinator.data[self._FIELD])
        return None


class TeleinfoSensorString(TeleinfoEntity):
    """ Teleinfo entity with string data. """

    @staticmethod
    def _convert_data(value: str):
        """ Convert data to native value format. """
        return value


class TeleinfoSensorInt(TeleinfoEntity):
    """ Teleinfo entity with integer data. """

    @staticmethod
    def _convert_data(value: str):
        """ Convert data to native value format. """
        return int(value)


class TeleinfoSensorIntKilo(TeleinfoEntity):
    """ Teleinfo entity with integer data. """

    @staticmethod
    def _convert_data(value: str):
        """ Convert data to native value format. """
        return int(value) / 1000


class TeleinfoSensorInfo(TeleinfoSensorString):
    """ Teleinfo information sensor. """


class TeleinfoSensorIndex(TeleinfoSensorIntKilo):
    """ Teleinfo index sensor. """
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR


class TeleinfoSensorCurrent(TeleinfoSensorInt):
    """ Teleinfo current sensor. """
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE


class TeleinfoSensorPower(TeleinfoSensorInt):
    """ Teleinfo power sensor. """
    _attr_device_class = SensorDeviceClass.APPARENT_POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfApparentPower.VOLT_AMPERE
