# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""
from unittest.mock import Mock

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import ATTRIBUTION
from custom_components.gismeteo.weather import GismeteoWeather
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant

from tests.const import FAKE_UNIQUE_ID


async def test_entity_initialization(hass: HomeAssistant):
    """Test entity initialization."""
    mock_api = Mock()
    mock_api.condition = Mock(return_value="asd")
    mock_api.attributes = {}

    coordinator = GismeteoDataUpdateCoordinator(hass, FAKE_UNIQUE_ID, mock_api)
    entity = GismeteoWeather(coordinator, "Test")

    assert entity.unique_id == FAKE_UNIQUE_ID
    assert entity.attribution == ATTRIBUTION
    assert entity.condition == "asd"
    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_pressure_unit == UnitOfPressure.MMHG
    assert entity.native_wind_speed_unit == UnitOfSpeed.METERS_PER_SECOND
