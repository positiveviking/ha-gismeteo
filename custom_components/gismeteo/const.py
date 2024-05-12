#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from datetime import timedelta
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.components.weather import ATTR_FORECAST_CONDITION
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    Platform,
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
PLATFORMS: Final = [Platform.SENSOR, Platform.WEATHER]

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
ATTR_WEATHER_POLLEN_BIRCH = "pollen_birch"
ATTR_WEATHER_POLLEN_GRASS = "pollen_grass"
ATTR_WEATHER_POLLEN_RAGWEED = "pollen_ragweed"
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

TYPE_WEATHER: Final = "weather"  # Deprecated
TYPE_CONDITION: Final = "condition"
TYPE_TEMPERATURE: Final = "temperature"
TYPE_TEMPERATURE_FEELS_LIKE: Final = "temperature_feels_like"  # Deprecated
TYPE_APPARENT_TEMPERATURE: Final = "apparent_temperature"
TYPE_HUMIDITY: Final = "humidity"
TYPE_PRESSURE: Final = "pressure"
TYPE_WIND_SPEED: Final = "wind_speed"
TYPE_WIND_BEARING: Final = "wind_bearing"
TYPE_CLOUDS: Final = "clouds"  # Deprecated
TYPE_CLOUD_COVERAGE: Final = "cloud_coverage"
TYPE_RAIN: Final = "rain"  # Deprecated
TYPE_RAIN_AMOUNT: Final = "rain_amount"
TYPE_SNOW: Final = "snow"  # Deprecated
TYPE_SNOW_AMOUNT: Final = "snow_amount"
TYPE_STORM: Final = "storm"
TYPE_GEOMAGNETIC: Final = "geomagnetic"  # Deprecated
TYPE_GEOMAGNETIC_FIELD: Final = "geomagnetic_field"
TYPE_WATER_TEMPERATURE: Final = "water_temperature"
TYPE_UV_INDEX: Final = "uv_index"
TYPE_POLLEN_BIRCH: Final = "pollen_birch"
TYPE_POLLEN_GRASS: Final = "pollen_grass"
TYPE_POLLEN_RAGWEED: Final = "pollen_ragweed"

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

PRECIPITATION_AMOUNT: Final = (0, 2, 6, 16)

DEVICE_CLASS_TPL: Final = DOMAIN + "__{}"

SENSOR_DESCRIPTIONS: Final = (
    SensorEntityDescription(
        key=TYPE_CONDITION,
        translation_key="condition",
        has_entity_name=True,
        device_class=DEVICE_CLASS_TPL.format("condition"),
    ),
    SensorEntityDescription(
        key=TYPE_TEMPERATURE,
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key=TYPE_APPARENT_TEMPERATURE,
        translation_key="apparent_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_HUMIDITY,
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key=TYPE_PRESSURE,
        translation_key="pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
    ),
    SensorEntityDescription(
        key=TYPE_WIND_SPEED,
        translation_key="wind_speed",
        icon="mdi:weather-windy",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_WIND_BEARING,
        translation_key="wind_bearing",
        icon="mdi:weather-windy",
        native_unit_of_measurement=DEGREE,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_CLOUD_COVERAGE,
        translation_key="cloud_coverage",
        icon="mdi:weather-partly-cloudy",
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_RAIN_AMOUNT,
        translation_key="rain_amount",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_SNOW_AMOUNT,
        translation_key="snow_amount",
        icon="mdi:weather-snowy",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_STORM,
        translation_key="storm",
        icon="mdi:weather-lightning",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_GEOMAGNETIC_FIELD,
        translation_key="geomagnetic_field",
        icon="mdi:magnet-on",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_WATER_TEMPERATURE,
        translation_key="water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_UV_INDEX,
        translation_key="uv_index",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_BIRCH,
        translation_key="pollen_birch",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_GRASS,
        translation_key="pollen_grass",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_RAGWEED,
        translation_key="pollen_ragweed",
        entity_registry_enabled_default=False,
    ),
)

FORECAST_SENSOR_DESCRIPTIONS: Final = (
    SensorEntityDescription(
        key=TYPE_CONDITION,
        translation_key="condition_forecast",
        has_entity_name=True,
        device_class=DEVICE_CLASS_TPL.format("condition"),
    ),
    SensorEntityDescription(
        key=TYPE_TEMPERATURE,
        translation_key="temperature_forecast",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key=TYPE_APPARENT_TEMPERATURE,
        translation_key="apparent_temperature_forecast",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_HUMIDITY,
        translation_key="humidity_forecast",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key=TYPE_PRESSURE,
        translation_key="pressure_forecast",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
    ),
    SensorEntityDescription(
        key=TYPE_WIND_SPEED,
        translation_key="wind_speed_forecast",
        icon="mdi:weather-windy",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_WIND_BEARING,
        translation_key="wind_bearing_forecast",
        icon="mdi:weather-windy",
        native_unit_of_measurement=DEGREE,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_CLOUD_COVERAGE,
        translation_key="cloud_coverage_forecast",
        icon="mdi:weather-partly-cloudy",
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_RAIN_AMOUNT,
        translation_key="rain_amount_forecast",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_SNOW_AMOUNT,
        translation_key="snow_amount_forecast",
        icon="mdi:weather-snowy",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_STORM,
        translation_key="storm_forecast",
        icon="mdi:weather-lightning",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_GEOMAGNETIC_FIELD,
        translation_key="geomagnetic_field_forecast",
        icon="mdi:magnet-on",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_WATER_TEMPERATURE,
        translation_key="water_temperature_forecast",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_UV_INDEX,
        translation_key="uv_index_forecast",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_BIRCH,
        translation_key="pollen_birch_forecast",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_GRASS,
        translation_key="pollen_grass_forecast",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=TYPE_POLLEN_RAGWEED,
        translation_key="pollen_ragweed_forecast",
        entity_registry_enabled_default=False,
    ),
)
