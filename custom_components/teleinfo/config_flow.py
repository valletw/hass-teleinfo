""" Config flow setup. """
from os.path import exists
from typing import Optional, Dict, Any
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import (
    CONF_NAME,
    CONF_DEVICE,
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_DEVICE
)


SCHEMA = vol.Schema({
    vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): str,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str
})


class TeleinfoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """ Config flow handler for teleinfo. """

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """ Manage user flow. """
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Check if serial port exists.
            if not exists(user_input[CONF_DEVICE]):
                errors["base"] = "invalid_serial"
            if not errors:
                # Input validated, configuration done, create entry.
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )
        # No user input, ask parameters.
        return self.async_show_form(
            step_id="user",
            data_schema=SCHEMA,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """ Get options flow. """
        return TeleinfoOptionsFlowHandler(config_entry)


class TeleinfoOptionsFlowHandler(config_entries.OptionsFlow):
    """ Options flow handler for teleinfo. """

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None):
        """ Manage the options. """
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Check if serial port exists.
            if not exists(user_input[CONF_DEVICE]):
                errors["base"] = "invalid_serial"
            if not errors:
                # Input validated, configuration update done, create entry.
                return self.async_create_entry(
                    title=self.config_entry.data.get(CONF_NAME),
                    data=user_input
                )
        return self.async_show_form(
            step_id="init",
            data_schema=SCHEMA,
            errors=errors
        )
