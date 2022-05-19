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
    ENERGY_KILO_WATT_HOUR,
    ELECTRIC_CURRENT_AMPERE,
    POWER_VOLT_AMPERE
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR
)


class TeleinfoEntity(CoordinatorEntity, SensorEntity):
    """ Teleinfo entity. """

    _attr_should_poll = False
    _attr_native_value = None

    def __init__(self, coordinator, uid: str, device: str, name: str, desc: str):
        super().__init__(coordinator)
        self.entity_id = f"{SENSOR}.{DOMAIN}_{device.lower()}_{name.lower()}"
        self._attr_unique_id = f"{uid}-{name.lower()}"
        self._attr_name = desc
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, uid)},
            ATTR_NAME: device,
            ATTR_MANUFACTURER: "EDF",
        }


class TeleinfoSensorString(TeleinfoEntity):
    """ Teleinfo entity with string data. """

    def set_data(self, value: str):
        """ Update entity with new value. """
        self._attr_native_value = value


class TeleinfoSensorInt(TeleinfoEntity):
    """ Teleinfo entity with integer data. """

    def set_data(self, value: str):
        """ Update entity with new value. """
        self._attr_native_value = int(value)


class TeleinfoSensorIntKilo(TeleinfoEntity):
    """ Teleinfo entity with integer data. """

    def set_data(self, value: str):
        """ Update entity with new value. """
        self._attr_native_value = int(value) / 1000


class TeleinfoSensorInfo(TeleinfoSensorString):
    """ Teleinfo information sensor. """


class TeleinfoSensorIndex(TeleinfoSensorIntKilo):
    """ Teleinfo index sensor. """
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR


class TeleinfoSensorCurrent(TeleinfoSensorInt):
    """ Teleinfo current sensor. """
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE


class TeleinfoSensorPower(TeleinfoSensorInt):
    """ Teleinfo power sensor. """
    _attr_device_class = SensorDeviceClass.APPARENT_POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = POWER_VOLT_AMPERE
