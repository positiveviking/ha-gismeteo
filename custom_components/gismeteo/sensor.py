#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from datetime import date, datetime
from decimal import Decimal
from functools import cached_property
import logging
from typing import Final

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.weather import (
    ATTR_FORECAST_APPARENT_TEMP,
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_CONDITION,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_MONITORED_CONDITIONS, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, StateType

from . import GismeteoDataUpdateCoordinator, _convert_yaml_config, deslugify
from .const import (
    ATTR_FORECAST_GEOMAGNETIC_FIELD,
    ATTR_FORECAST_RAIN_AMOUNT,
    ATTR_FORECAST_SNOW_AMOUNT,
    ATTRIBUTION,
    CONF_FORECAST_DAYS,
    CONF_PLATFORM_FORMAT,
    COORDINATOR,
    DOMAIN,
    DOMAIN_YAML,
    FORECAST_MODE_DAILY,
    FORECAST_SENSOR_DESCRIPTIONS,
    SENSOR_DESCRIPTIONS,
)
from .entity import GismeteoEntity

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({})

DEPRECATED_SENSOR_TYPES: Final = {
    "weather": ATTR_FORECAST_CONDITION,
    "temperature_feels_like": ATTR_FORECAST_APPARENT_TEMP,
    "clouds": ATTR_FORECAST_CLOUD_COVERAGE,
    "rain": ATTR_FORECAST_RAIN_AMOUNT,
    "snow": ATTR_FORECAST_SNOW_AMOUNT,
    "geomagnetic": ATTR_FORECAST_GEOMAGNETIC_FIELD,
}


def _fix_types(types: list[str], warn=True) -> list[str]:
    """Remove unwanted values from types."""
    types = set(types)

    dep_types = ["forecast", "pressure_mmhg"]
    dep_types.extend(DEPRECATED_SENSOR_TYPES.keys())
    for stype in dep_types:
        if stype in types:
            types.remove(stype)

            if stype in DEPRECATED_SENSOR_TYPES:
                types.add(DEPRECATED_SENSOR_TYPES[stype])
                if warn:
                    _LOGGER.warning(
                        'The "%s" condition is deprecated,'
                        ' please replace it with "%s"',
                        stype,
                        DEPRECATED_SENSOR_TYPES[stype],
                    )

    return [x.key for x in SENSOR_DESCRIPTIONS if x.key in types]


def _gen_entities(
    location_name: str,
    coordinator: GismeteoDataUpdateCoordinator,
    config: ConfigType,
    warn: bool,
):
    """Generate entities."""
    entities = []

    types = _fix_types(
        config.get(CONF_MONITORED_CONDITIONS, [x.key for x in SENSOR_DESCRIPTIONS]),
        warn=warn,
    )

    entities.extend(
        [
            GismeteoSensor(coordinator, desc, location_name)
            for desc in SENSOR_DESCRIPTIONS
            if desc.key in types
        ]
    )

    days = config.get(CONF_FORECAST_DAYS)
    if days is not None:
        for day in range(days + 1):
            entities.extend(
                [
                    GismeteoSensor(coordinator, desc, location_name, day)
                    for desc in FORECAST_SENSOR_DESCRIPTIONS
                    if desc.key in types
                ]
            )

    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Add Gismeteo sensor entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, cfg in hass.data[DOMAIN_YAML].items():
            cfg = _convert_yaml_config(cfg)

            if cfg.get(CONF_PLATFORM_FORMAT.format(Platform.SENSOR), False) is False:
                continue  # pragma: no cover

            location_name = cfg.get(CONF_NAME, deslugify(uid))
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            entities.extend(_gen_entities(location_name, coordinator, cfg, True))

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: ConfigType
        config.update(config_entry.options)

        if config.get(CONF_PLATFORM_FORMAT.format(Platform.SENSOR), False) is False:
            return  # pragma: no cover

        location_name = config[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        entities.extend(_gen_entities(location_name, coordinator, config, False))

    async_add_entities(entities)


class GismeteoSensor(GismeteoEntity, SensorEntity):
    """Implementation of an Gismeteo sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GismeteoDataUpdateCoordinator,
        description: SensorEntityDescription,
        location_name: str,
        day: int | None = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, location_name)

        self.entity_description = description
        # if day:
        # self.entity_description.translation_key += "-day"

        self._attr_unique_id = (
            f"{coordinator.unique_id}-{description.key}"
            if day is None
            else f"{coordinator.unique_id}-{day}-{description.key}"
        ).lower()
        self._attr_translation_placeholders = {
            "location_name": location_name,
            "type": description.key,
            "day": day,
        }
        self._attr_extra_state_attributes = self._gismeteo.attributes

        self._day = day

    @cached_property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        try:

            return getattr(self._gismeteo, self.entity_description.key)(
                self._gismeteo.forecast_data(self._day, FORECAST_MODE_DAILY)
                if self._day is not None
                else None
            )

        except KeyError:  # pragma: no cover
            _LOGGER.warning(
                "Condition is currently not available: %s", self.entity_description.key
            )
            return None
