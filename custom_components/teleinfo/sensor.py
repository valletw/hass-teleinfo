""" Teleinfo sensors. """
import asyncio
import logging
from typing import TypedDict
from serial import SerialException
import serial_asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN, NAME, CONF_NAME, CONF_DEVICE
)
from .entities import (
    TeleinfoSensorInfo,
    TeleinfoSensorIndex,
    TeleinfoSensorCurrent,
    TeleinfoSensorPower
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    """ Setup sensor platform. """
    name = entry.data.get(CONF_NAME)
    port = entry.data.get(CONF_DEVICE)
    coordinator = TeleinfoCoordinator(hass, name, port, entry.entry_id)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    async_add_devices(coordinator.sensors.values())
    await coordinator.async_added_to_hass()


class TeleinfoSensors(TypedDict):
    """ Teleinfo sensors. """
    adco: TeleinfoSensorInfo
    optarif: TeleinfoSensorInfo
    ptec: TeleinfoSensorInfo
    hhphc: TeleinfoSensorInfo
    base: TeleinfoSensorIndex
    hchc: TeleinfoSensorIndex
    hchp: TeleinfoSensorIndex
    isousc: TeleinfoSensorCurrent
    iinst: TeleinfoSensorCurrent
    imax: TeleinfoSensorCurrent
    adps: TeleinfoSensorCurrent
    papp: TeleinfoSensorPower


class TeleinfoCoordinator(DataUpdateCoordinator):
    """ Teleinfo coordinator """

    SERIAL_CFG = {
        "baudrate": 1200,
        "bytesize": 7,
        "parity": 'E',
        "stopbits": 1,
        "rtscts": 1
    }
    FRAME_START = "\x02"
    FRAME_END = "\x03"

    def __init__(self, hass: HomeAssistant, name: str, port: str, uid: str):
        super().__init__(
            hass, _LOGGER, name=NAME,
        )
        self.port = port
        self.sensors: TeleinfoSensors = {
            "adco": TeleinfoSensorInfo(uid, name, "ADCO", "Adresse d'itentification"),
            "optarif": TeleinfoSensorInfo(uid, name, "OPTARIF", "Option tarifaire"),
            "ptec": TeleinfoSensorInfo(uid, name, "PTEC", "Période tarifaire en cours"),
            "hhphc": TeleinfoSensorInfo(uid, name, "HHPHC", "Horaire HP/HC"),
            "base": TeleinfoSensorIndex(uid, name, "BASE", "Index option Base"),
            "hchc": TeleinfoSensorIndex(uid, name, "HCHC", "Index option Heure Creuse"),
            "hchp": TeleinfoSensorIndex(uid, name, "HCHP", "Index option Heure Pleine"),
            "isousc": TeleinfoSensorCurrent(uid, name, "ISOUSC", "Intensité souscrite"),
            "iinst": TeleinfoSensorCurrent(uid, name, "IINST", "Intensité instantanée"),
            "imax": TeleinfoSensorCurrent(uid, name, "IMAX", "Intensité maximale"),
            "adps": TeleinfoSensorCurrent(uid, name, "ADPS", "Avertissement de dépassement"),
            "papp": TeleinfoSensorPower(uid, name, "PAPP", "Puissance apparente")
        }
        self.serial_task = None
        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, self.serial_stop())

    async def async_added_to_hass(self):
        """ Handle when an entity will be added. """
        self.serial_task = self.hass.loop.create_task(
            self.serial_read()
        )

    async def serial_stop(self):
        """ Close serial connection. """
        if self.serial_task:
            self.serial_task.cancel()

    async def serial_read(self):
        """ Serial data listener. """
        _LOGGER.debug("Serial initialisation")
        try:
            serial, _ = await serial_asyncio.open_serial_connection(
                url=self.port, **self.SERIAL_CFG
            )
        except SerialException as exp:
            _LOGGER.error(
                "Unable to connect to serial device '%s': %s",
                self.port, exp
            )
            return
        # Clear first data.
        await serial.readline()
        _LOGGER.debug("Serial processing")
        frame_processing = False
        while True:
            # Read data, and remove trailing characters.
            try:
                line = await serial.readline()
            except SerialException as exp:
                _LOGGER.error("Error during serial read: %s", exp)
                asyncio.sleep(1)
                continue
            line = line.decode("ascii").strip()
            # Look for start frame.
            if not frame_processing and self.FRAME_START in line:
                frame_processing = True
                _LOGGER.debug("Start frame")
                continue
            # Parse frame content.
            if frame_processing:
                # Look for end frame.
                if self.FRAME_END in line:
                    frame_processing = False
                    _LOGGER.debug("End frame")
                # Decode value.
                else:
                    name, value = line.split()[0:2]
                    _LOGGER.debug("Read '%s' = '%s'", name, value)
                    # Update sensor value.
                    name = name.lower()
                    if name in self.sensors.keys():
                        self.sensors[name].set_data(value)
                        self.sensors[name].async_schedule_update_ha_state()
                    else:
                        _LOGGER.debug("Data not managed")
