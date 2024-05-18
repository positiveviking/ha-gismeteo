# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""
from unittest.mock import Mock, patch

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import ATTRIBUTION, CONF_FORECAST_DAYS
from custom_components.gismeteo.sensor import GismeteoSensor, _gen_entities
from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.components.weather import ATTR_FORECAST_TEMP
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from tests.const import FAKE_UNIQUE_ID


@patch("custom_components.gismeteo.GismeteoDataUpdateCoordinator")
async def test__gen_entities(mock_coordinator):
    """Test _gen_entities function."""
    res = _gen_entities("Test location", mock_coordinator, {})
    assert len(res) == 20

    res = _gen_entities("Test location", mock_coordinator, {CONF_FORECAST_DAYS: 0})
    assert len(res) == 41

    res = _gen_entities("Test location", mock_coordinator, {CONF_FORECAST_DAYS: 1})
    assert len(res) == 62


async def test_entity_initialization(hass: HomeAssistant):
    """Test entity initialization."""
    mock_api = Mock()
    mock_api.temperature = Mock(return_value=123)
    mock_api.attributes = {}

    coordinator = GismeteoDataUpdateCoordinator(hass, FAKE_UNIQUE_ID, mock_api)
    sensor = GismeteoSensor(
        coordinator,
        SensorEntityDescription(
            key=ATTR_FORECAST_TEMP,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        ),
        "Test",
    )

    assert sensor.unique_id == f"{FAKE_UNIQUE_ID}-temperature"
    assert sensor.should_poll is False
    assert sensor.available is True
    assert sensor.native_value == 123
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.icon is None
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.attribution == ATTRIBUTION
