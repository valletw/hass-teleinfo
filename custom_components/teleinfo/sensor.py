""" Teleinfo sensors. """
import asyncio
import logging
from typing import List
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
    TeleinfoEntity,
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
    async_add_devices(coordinator.sensors)
    await coordinator.async_added_to_hass()


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
        self.data = {}
        self.sensors: List[TeleinfoEntity] = [
            TeleinfoSensorADCO(self, uid, name),
            TeleinfoSensorOPTARIF(self, uid, name),
            TeleinfoSensorPTEC(self, uid, name),
            TeleinfoSensorHHPHC(self, uid, name),
            TeleinfoSensorBASE(self, uid, name),
            TeleinfoSensorHCHC(self, uid, name),
            TeleinfoSensorHCHP(self, uid, name),
            TeleinfoSensorISOUSC(self, uid, name),
            TeleinfoSensorIINST(self, uid, name),
            TeleinfoSensorIMAX(self, uid, name),
            TeleinfoSensorADPS(self, uid, name),
            TeleinfoSensorPAPP(self, uid, name)
        ]
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
        data = {}
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
                data.clear()
                _LOGGER.debug("Start frame")
                continue
            # Parse frame content.
            if frame_processing:
                # Look for end frame.
                if self.FRAME_END in line:
                    frame_processing = False
                    _LOGGER.debug("End frame")
                    # Update coordinator data.
                    self.async_set_updated_data(data)
                    # Trigger sensors state update.
                    for sensor in self.sensors:
                        sensor.async_schedule_update_ha_state()
                # Decode value.
                else:
                    name, value = line.split()[0:2]
                    _LOGGER.debug("Read '%s' = '%s'", name, value)
                    # Store value.
                    data[name] = value


class TeleinfoSensorADCO(TeleinfoSensorInfo):
    """ Teleinfo sensor ADCO. """
    _FIELD = "ADCO"
    _DESC = "Adresse d'itentification"


class TeleinfoSensorOPTARIF(TeleinfoSensorInfo):
    """ Teleinfo sensor OPTARIF. """
    _FIELD = "OPTARIF"
    _DESC = "Option tarifaire"


class TeleinfoSensorPTEC(TeleinfoSensorInfo):
    """ Teleinfo sensor PTEC. """
    _FIELD = "PTEC"
    _DESC = "Période tarifaire en cours"


class TeleinfoSensorHHPHC(TeleinfoSensorInfo):
    """ Teleinfo sensor HHPHC. """
    _FIELD = "HHPHC"
    _DESC = "Horaire HP/HC"


class TeleinfoSensorBASE(TeleinfoSensorIndex):
    """ Teleinfo sensor BASE. """
    _FIELD = "BASE"
    _DESC = "Index option Base"


class TeleinfoSensorHCHC(TeleinfoSensorIndex):
    """ Teleinfo sensor HCHC. """
    _FIELD = "HCHC"
    _DESC = "Index option Heure Creuse"


class TeleinfoSensorHCHP(TeleinfoSensorIndex):
    """ Teleinfo sensor HCHP. """
    _FIELD = "HCHP"
    _DESC = "Index option Heure Pleine"


class TeleinfoSensorISOUSC(TeleinfoSensorCurrent):
    """ Teleinfo sensor ISOUSC. """
    _FIELD = "ISOUSC"
    _DESC = "Intensité souscrite"


class TeleinfoSensorIINST(TeleinfoSensorCurrent):
    """ Teleinfo sensor IINST. """
    _FIELD = "IINST"
    _DESC = "Intensité instantanée"


class TeleinfoSensorIMAX(TeleinfoSensorCurrent):
    """ Teleinfo sensor IMAX. """
    _FIELD = "IMAX"
    _DESC = "Intensité maximale"


class TeleinfoSensorADPS(TeleinfoSensorCurrent):
    """ Teleinfo sensor ADPS. """
    _FIELD = "ADPS"
    _DESC = "Avertissement de dépassement"


class TeleinfoSensorPAPP(TeleinfoSensorPower):
    """ Teleinfo sensor PAPP. """
    _FIELD = "PAPP"
    _DESC = "Puissance apparente"
