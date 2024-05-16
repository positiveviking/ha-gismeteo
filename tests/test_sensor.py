# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""
from unittest.mock import Mock, patch

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import ATTRIBUTION
from custom_components.gismeteo.sensor import GismeteoSensor, _fix_types, _gen_entities
from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.components.weather import ATTR_FORECAST_TEMP
from homeassistant.const import CONF_MONITORED_CONDITIONS, UnitOfTemperature
from homeassistant.core import HomeAssistant

from tests.const import FAKE_UNIQUE_ID


async def test__fix_types(caplog):
    """Test _fix_types function."""
    caplog.clear()
    res = _fix_types([])
    assert res == []
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_types(["qwe", "asd"])
    assert res == []
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_types(["humidity", "temperature"])
    assert res == ["temperature", "humidity"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_types(
        ["humidity", "temperature", "pressure", "forecast", "pressure_mmhg"]
    )
    assert res == ["temperature", "humidity", "pressure"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_types(["humidity", "temperature", "weather"])
    assert res == ["condition", "temperature", "humidity"]
    assert len(caplog.records) == 1

    caplog.clear()
    res = _fix_types(["humidity", "temperature", "weather"], False)
    assert res == ["condition", "temperature", "humidity"]
    assert len(caplog.records) == 0


@patch("custom_components.gismeteo.GismeteoDataUpdateCoordinator")
async def test__gen_entities(mock_coordinator):
    """Test _gen_entities function."""
    res = _gen_entities("Test location", mock_coordinator, {}, False)
    assert len(res) == 20

    res = _gen_entities(
        "Test location",
        mock_coordinator,
        {CONF_MONITORED_CONDITIONS: ["temperature", "humidity"]},
        False,
    )
    assert len(res) == 2


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
