#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from datetime import timedelta
from typing import Final

from homeassistant.components.sensor import DOMAIN as SENSOR, SensorDeviceClass
from homeassistant.components.weather import ATTR_FORECAST_CONDITION, DOMAIN as WEATHER
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

# Base component constants
NAME: Final = "Gismeteo"
DOMAIN: Final = "gismeteo"
VERSION: Final = "3.0.0.dev0"
ATTRIBUTION: Final = "Data provided by Gismeteo"
ISSUE_URL: Final = "https://github.com/Limych/ha-gismeteo/issues"
#
DOMAIN_YAML: Final = f"{DOMAIN}_yaml"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Platforms
PLATFORMS: Final = [SENSOR, WEATHER]

# Configuration and options
CONF_CACHE_DIR: Final = "cache_dir"
CONF_FORECAST: Final = "forecast"
CONF_FORECAST_DAYS: Final = "forecast_days"
CONF_PLATFORMS: Final = "platforms"
CONF_YAML: Final = "_yaml"
CONF_PLATFORM_FORMAT: Final = "_platform_{}"

FORECAST_MODE_HOURLY: Final = "hourly"
FORECAST_MODE_DAILY: Final = "daily"

# Defaults
DEFAULT_NAME: Final = "Gismeteo"

# Attributes
ATTR_LAST_UPDATED: Final = "last_updated"
#
ATTR_SUNRISE: Final = "sunrise"
ATTR_SUNSET: Final = "sunset"
#
ATTR_WEATHER_CONDITION: Final = ATTR_FORECAST_CONDITION
ATTR_WEATHER_CLOUDINESS: Final = "cloudiness"
ATTR_WEATHER_PRECIPITATION_TYPE: Final = "precipitation_type"
ATTR_WEATHER_PRECIPITATION_AMOUNT: Final = "precipitation_amount"
ATTR_WEATHER_PRECIPITATION_INTENSITY: Final = "precipitation_intensity"
ATTR_WEATHER_STORM: Final = "storm"
ATTR_WEATHER_GEOMAGNETIC_FIELD: Final = "gm_field"
ATTR_WEATHER_PHENOMENON: Final = "phenomenon"
ATTR_WEATHER_WATER_TEMPERATURE: Final = "water_temperature"
ATTR_WEATHER_ALLERGY_BIRCH = "allergy_birch"
ATTR_WEATHER_UV_INDEX = "uv_index"
#
ATTR_FORECAST_HUMIDITY: Final = "humidity"
ATTR_FORECAST_PRESSURE: Final = "pressure"
ATTR_FORECAST_CLOUDINESS: Final = ATTR_WEATHER_CLOUDINESS
ATTR_FORECAST_PRECIPITATION_TYPE: Final = ATTR_WEATHER_PRECIPITATION_TYPE
ATTR_FORECAST_PRECIPITATION_AMOUNT: Final = ATTR_WEATHER_PRECIPITATION_AMOUNT
ATTR_FORECAST_PRECIPITATION_INTENSITY: Final = ATTR_WEATHER_PRECIPITATION_INTENSITY
ATTR_FORECAST_STORM: Final = ATTR_WEATHER_STORM
ATTR_FORECAST_GEOMAGNETIC_FIELD: Final = ATTR_WEATHER_GEOMAGNETIC_FIELD
ATTR_FORECAST_PHENOMENON: Final = ATTR_WEATHER_PHENOMENON
#
ATTR_LAT: Final = "lat"
ATTR_LON: Final = "lon"

COORDINATOR: Final = "coordinator"
UNDO_UPDATE_LISTENER: Final = "undo_update_listener"

ENDPOINT_URL: Final = "https://services.gismeteo.ru/inform-service/inf_chrome"
#
PARSER_URL_FORMAT: Final = "https://www.gismeteo.ru/weather-{}/10-days/"
PARSER_USER_AGENT: Final = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81"
)

UPDATE_INTERVAL: Final = timedelta(minutes=5)
PARSED_UPDATE_INTERVAL: Final = timedelta(minutes=61)
LOCATION_MAX_CACHE_INTERVAL: Final = timedelta(days=7)
FORECAST_MAX_CACHE_INTERVAL: Final = timedelta(hours=3)

CONDITION_FOG_CLASSES: Final = [
    11,
    12,
    28,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    120,
    130,
    131,
    132,
    133,
    134,
    135,
    528,
]

MMHG2HPA: Final = 1.333223684
MS2KMH: Final = 3.6

PRECIPITATION_AMOUNT: Final = (0, 2, 6, 16)

DEVICE_CLASS_TPL: Final = DOMAIN + "__{}"

SENSOR_TYPES: Final = {
    "weather": {},  # => condition
    "condition": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TPL.format("condition"),
        ATTR_ICON: None,
        ATTR_NAME: "Condition",
        ATTR_UNIT_OF_MEASUREMENT: None,
    },
    "temperature": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Temperature",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfTemperature.CELSIUS,
    },
    "temperature_feels_like": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Temperature Feels Like",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfTemperature.CELSIUS,
    },
    "humidity": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.HUMIDITY,
        ATTR_ICON: None,
        ATTR_NAME: "Humidity",
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "pressure": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.PRESSURE,
        ATTR_ICON: None,
        ATTR_NAME: "Pressure",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfPressure.HPA,
    },
    "wind_speed": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_NAME: "Wind speed",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfSpeed.METERS_PER_SECOND,
    },
    "wind_bearing": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_NAME: "Wind bearing",
        ATTR_UNIT_OF_MEASUREMENT: DEGREE,
    },
    "clouds": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-partly-cloudy",
        ATTR_NAME: "Cloud coverage",
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "rain": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_NAME: "Rain",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfLength.MILLIMETERS,
    },
    "snow": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-snowy",
        ATTR_NAME: "Snow",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfLength.MILLIMETERS,
    },
    "storm": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-lightning",
        ATTR_NAME: "Storm",
        ATTR_UNIT_OF_MEASUREMENT: None,
    },
    "geomagnetic": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:magnet-on",
        ATTR_NAME: "Geomagnetic field",
        ATTR_UNIT_OF_MEASUREMENT: "",
    },
    "water_temperature": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Water Temperature",
        ATTR_UNIT_OF_MEASUREMENT: UnitOfTemperature.CELSIUS,
    },
}
FORECAST_SENSOR_TYPE: Final = {
    ATTR_DEVICE_CLASS: DEVICE_CLASS_TPL.format("condition"),
    ATTR_ICON: None,
    ATTR_NAME: "3h Forecast",
    ATTR_UNIT_OF_MEASUREMENT: None,
}
