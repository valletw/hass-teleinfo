""" Constants for teleinfo. """
# Base constants.
NAME = "Tele Information"
DOMAIN = "teleinfo"
DOMAIN_DATA = f"{DOMAIN}_data"
ATTRIBUTION = "Data provided by serial TIC reader (French electric meter)."

# Device classes.

# Platforms.
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options.
CONF_NAME = "name"
CONF_DEVICE = "serial"

# Defaults.
DEFAULT_NAME = DOMAIN
DEFAULT_DEVICE = ""
