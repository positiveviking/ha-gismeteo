# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""
from datetime import datetime
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, patch

from aiohttp import ClientSession
import pytest
from pytest import raises
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.gismeteo.api import (
    ApiError,
    GismeteoApiClient,
    InvalidCoordinatesError,
)
from custom_components.gismeteo.const import (
    ATTR_FORECAST_IS_STORM,
    ATTR_FORECAST_PHENOMENON,
    ATTR_FORECAST_PRECIPITATION_INTENSITY,
    ATTR_FORECAST_PRECIPITATION_TYPE,
    ATTR_SUNRISE,
    CONDITION_FOG_CLASSES,
    FORECAST_MODE_DAILY,
)
from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
    ATTR_CONDITION_WINDY_VARIANT,
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
)
from homeassistant.const import ATTR_ID, STATE_UNKNOWN
from homeassistant.util import dt as dt_util

LATITUDE = 52.0677904
LONGITUDE = 19.4795644
LOCATION_KEY = 3546

MOCK_NOW = dt_util.parse_datetime("2021-02-21T16:16:00+03:00")
TZ180 = dt_util.get_time_zone("Europe/Moscow")


@pytest.fixture(autouse=True)
def patch_time():
    """Patch time functions."""
    with (
        patch.object(dt_util, "now", return_value=MOCK_NOW),
        patch("time.time", return_value=MOCK_NOW.timestamp()),
    ):
        yield


async def test__valid_coordinates():
    """Test with valid and invalid location data."""
    lat_valid = (0, 15, 90, -32, -90, LATITUDE)
    lon_valid = (0, 35, 90, 154, 180, -78, -90, -135, -180, LONGITUDE)
    lat_invalid = (90.1, -90.1, 641, -94)
    lon_invalid = (180.1, -180.1, 235, -4566)

    for lat in lat_valid:
        for lon in lon_valid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is True
        for lon in lon_invalid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False
    for lat in lat_invalid:
        for lon in lon_valid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False
        for lon in lon_invalid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False

    async with ClientSession() as client:
        with raises(InvalidCoordinatesError):
            GismeteoApiClient(client, latitude=lat_invalid[0], longitude=lon_invalid[0])


async def test__get():
    """Test _get service method."""
    data = {"qwe": 123, "asd": "sdf", "zxc": "789"}

    assert GismeteoApiClient._get(data, "qwe") == 123
    assert GismeteoApiClient._get(data, "asd") == "sdf"
    assert GismeteoApiClient._get(data, "asd", int) is None
    assert GismeteoApiClient._get(data, "zxc") == "789"
    assert GismeteoApiClient._get(data, "zxc") != 789
    assert GismeteoApiClient._get(data, "zxc", int) == 789


@patch("aiohttp.ClientSession.get")
async def test__async_get_data(mock_get):
    """Test with valid location data."""
    mock_get.return_value.__aenter__.return_value.status = HTTPStatus.OK
    mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="qwe")
    #
    async with ClientSession() as client:
        gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
        city_id = await gismeteo._async_get_data("some_url")

    assert city_id == "qwe"

    mock_get.return_value.__aenter__.return_value.status = 404
    #
    async with ClientSession() as client:
        gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
        with raises(ApiError):
            await gismeteo._async_get_data("some_url")


async def test_async_update_location():
    """Test with valid location data."""
    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=load_fixture("location.xml"),
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=0, longitude=0)

            assert ATTR_ID not in gismeteo.attributes

            await gismeteo.async_update_location()

    assert ATTR_ID not in gismeteo.attributes

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=load_fixture("location.xml"),
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)

            assert ATTR_ID not in gismeteo.attributes

            await gismeteo.async_update_location()

    assert gismeteo.attributes[ATTR_ID] == 167413

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=None,
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
            with raises(ApiError):
                await gismeteo.async_update_location()

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value="qwe",
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
            with raises(ApiError):
                await gismeteo.async_update_location()


def test__get_utime():
    """Test _get_utime service method."""
    assert GismeteoApiClient._get_utime("2021-02-21T16:00:00", 180) == datetime(
        2021, 2, 21, 16, 0, tzinfo=TZ180
    )
    assert GismeteoApiClient._get_utime("2021-02-21T16:00:00", 0) == datetime(
        2021, 2, 21, 16, 0, tzinfo=dt_util.UTC
    )
    assert GismeteoApiClient._get_utime("2021-02-21", 180) == datetime(
        2021, 2, 21, tzinfo=TZ180
    )
    assert GismeteoApiClient._get_utime("2021-02-21", 0) == datetime(
        2021, 2, 21, tzinfo=dt_util.UTC
    )

    with raises(ValueError):
        GismeteoApiClient._get_utime("2021-02-", 0)


async def test_async_get_forecast():
    """Test parse data from Gismeteo main site."""
    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value="test data",
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=0, longitude=0)

            data = await gismeteo.async_get_forecast()

    assert data == ""

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value="test data",
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, location_key=LOCATION_KEY)

            data = await gismeteo.async_get_forecast()

    assert data == "test data"


async def test_async_get_parsed(gismeteo_api):
    """Test parse data from Gismeteo main site."""
    async with ClientSession() as client:
        gismeteo = GismeteoApiClient(client, location_key=LOCATION_KEY)

        data = await gismeteo.async_get_parsed()

        expected_data = {
            datetime(2021, 2, 21, tzinfo=TZ180): {
                "geomagnetic": "7",
                "humidity": "61",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "2",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0,3",
                "radiation": "2",
                "roadcondition": "Сухая дорога",
                "wind-direction": "С",
                "wind-gust": "–",
                "wind-speed": "2",
            },
            datetime(2021, 2, 22, tzinfo=TZ180): {
                "geomagnetic": "6",
                "humidity": "51",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "2",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "4",
                "roadcondition": "Сухая дорога",
                "wind-direction": "С",
                "wind-gust": "4",
                "wind-speed": "1",
            },
            datetime(2021, 2, 23, tzinfo=TZ180): {
                "geomagnetic": "4",
                "humidity": "51",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "2",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "3",
                "roadcondition": "Сухая дорога",
                "wind-direction": "СЗ",
                "wind-gust": "4",
                "wind-speed": "1",
            },
            datetime(2021, 2, 24, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "48",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "1",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "5",
                "roadcondition": "Сухая дорога",
                "wind-direction": "СЗ",
                "wind-gust": "4",
                "wind-speed": "1",
            },
            datetime(2021, 2, 25, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "48",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "1",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "7",
                "roadcondition": "Нет данных",
                "wind-direction": "СЗ",
                "wind-gust": "4",
                "wind-speed": "1",
            },
            datetime(2021, 2, 26, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "65",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "3",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "5,9",
                "radiation": "1",
                "roadcondition": "Нет данных",
                "wind-direction": "С",
                "wind-gust": "4",
                "wind-speed": "1",
            },
            datetime(2021, 2, 27, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "66",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "2",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "7",
                "roadcondition": "Нет данных",
                "wind-direction": "С",
                "wind-gust": "6",
                "wind-speed": "2",
            },
            datetime(2021, 2, 28, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "56",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "0",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "7",
                "roadcondition": "Нет данных",
                "wind-direction": "СЗ",
                "wind-gust": "3",
                "wind-speed": "1",
            },
            datetime(2021, 3, 1, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "55",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "–",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "6",
                "roadcondition": "Нет данных",
                "wind-direction": "СЗ",
                "wind-gust": "4",
                "wind-speed": "2",
            },
            datetime(2021, 3, 2, tzinfo=TZ180): {
                "geomagnetic": "2",
                "humidity": "54",
                "icon-snow": "–",
                "icon-tooltip": None,
                "pollen-birch": "–",
                "pollen-grass": "–",
                "pollen-ragweed": "–",
                "precipitation-bars": "0",
                "radiation": "6",
                "roadcondition": "Нет данных",
                "wind-direction": "З",
                "wind-gust": "5",
                "wind-speed": "2",
            },
        }

        assert data == expected_data


async def init_gismeteo(
    location_key: int | None = LOCATION_KEY,
    data: Any = False,
):
    """Prepare Gismeteo object."""
    forecast_data = data if data is not False else load_fixture("forecast.xml")
    forecast_parsed_data = load_fixture("forecast_parsed.html")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        return (
            forecast_data if args[0].find("/forecast/") >= 0 else forecast_parsed_data
        )

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(
                client,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                location_key=location_key,
                params={
                    "timezone": "UTC",
                },
            )

            assert not gismeteo.current_data
            assert not gismeteo.forecast_data(0)

            if location_key is None or data is not False:
                assert await gismeteo.async_update() is False
                assert not gismeteo.current_data
                assert not gismeteo.forecast_data(0)
            else:
                assert await gismeteo.async_update() is True
                assert gismeteo.current_data
                assert gismeteo.forecast_data(0)

    return gismeteo


async def test_api_init():
    """Test data update."""
    gismeteo = await init_gismeteo()

    expected_current = {
        "sunrise": datetime(2021, 2, 21, 10, 39, tzinfo=TZ180),
        "sunset": datetime(2021, 2, 21, 20, 47, tzinfo=TZ180),
        "condition": "Mainly cloudy, light snow",
        "native_temperature": -7.0,
        "native_pressure": 746,
        "humidity": 86,
        "native_wind_speed": 3,
        "wind_bearing": 5,
        "cloud_coverage": 3,
        "precipitation_type": 2,
        "precipitation_amount": 0.3,
        "precipitation_intensity": 1,
        "is_storm": False,
        "geomagnetic_field": 3,
        "phenomenon": 71,
        "water_temperature": 3.0,
    }
    expected_forecast = {
        "datetime": datetime(2021, 2, 21, 15, 0, tzinfo=TZ180),
        "sunrise": datetime(2021, 2, 21, 10, 39, tzinfo=TZ180),
        "sunset": datetime(2021, 2, 21, 20, 47, tzinfo=TZ180),
        "is_daytime": True,
        "condition": "Mainly cloudy, very heavy snow",
        "cloud_coverage": 3,
        "humidity": 86,
        "precipitation_amount": 2.2,
        "precipitation_intensity": 3,
        "precipitation_type": 2,
        "native_pressure": 746,
        "is_storm": False,
        "native_temperature": -7,
        "wind_bearing": 5,
        "native_wind_gust_speed": None,
        "native_wind_speed": 3,
        "geomagnetic_field": 3,
        "pollen_birch": 2,
        "pollen_grass": None,
        "pollen_ragweed": None,
        "uv_index": 2,
        "road_condition": "Сухая дорога",
    }

    assert gismeteo.attributes == {"id": LOCATION_KEY}
    assert gismeteo.current_data == expected_current
    assert gismeteo.forecast_data(0) == expected_forecast


async def test_async_update():
    """Test data update."""
    gismeteo = await init_gismeteo()

    assert gismeteo.current_data[ATTR_FORECAST_CLOUD_COVERAGE] == 3
    assert gismeteo.current_data[ATTR_FORECAST_HUMIDITY] == 86
    assert gismeteo.current_data[ATTR_FORECAST_PHENOMENON] == 71

    with raises(ApiError):
        await init_gismeteo(location_key=None)
    with raises(ApiError):
        await init_gismeteo(data=None)
    with raises(ApiError):
        await init_gismeteo(data="qwe")


async def test_condition():
    """Test condition."""
    gismeteo = await init_gismeteo()

    assert gismeteo.condition() == ATTR_CONDITION_SNOWY
    assert gismeteo.condition(gismeteo.current_data) == ATTR_CONDITION_SNOWY

    gismeteo_d = await init_gismeteo(FORECAST_MODE_DAILY)
    data = gismeteo.current_data

    data[ATTR_FORECAST_CLOUD_COVERAGE] = None
    data[ATTR_FORECAST_PRECIPITATION_TYPE] = 0

    assert gismeteo.condition(data) is None
    assert gismeteo_d.condition(data) is None

    data[ATTR_FORECAST_CLOUD_COVERAGE] = 0

    assert gismeteo.condition(data) == ATTR_CONDITION_SUNNY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_SUNNY

    tmp = data[ATTR_SUNRISE]
    data[ATTR_SUNRISE] = dt_util.now().replace(hour=23, minute=59, second=59)

    assert gismeteo.condition(data) == ATTR_CONDITION_CLEAR_NIGHT
    assert gismeteo_d.condition(data) == ATTR_CONDITION_CLEAR_NIGHT

    data[ATTR_SUNRISE] = tmp

    data[ATTR_FORECAST_CLOUD_COVERAGE] = 1

    assert gismeteo.condition(data) == ATTR_CONDITION_PARTLYCLOUDY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_PARTLYCLOUDY

    data[ATTR_FORECAST_CLOUD_COVERAGE] = 2

    assert gismeteo.condition(data) == ATTR_CONDITION_PARTLYCLOUDY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_PARTLYCLOUDY

    data[ATTR_FORECAST_CLOUD_COVERAGE] = 3

    assert gismeteo.condition(data) == ATTR_CONDITION_CLOUDY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_CLOUDY

    data[ATTR_FORECAST_IS_STORM] = True

    assert gismeteo.condition(data) == ATTR_CONDITION_LIGHTNING
    assert gismeteo_d.condition(data) == ATTR_CONDITION_LIGHTNING

    data[ATTR_FORECAST_PRECIPITATION_TYPE] = 1

    assert gismeteo.condition(data) == ATTR_CONDITION_LIGHTNING_RAINY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_LIGHTNING_RAINY

    data[ATTR_FORECAST_IS_STORM] = False

    assert gismeteo.condition(data) == ATTR_CONDITION_RAINY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_RAINY

    data[ATTR_FORECAST_PRECIPITATION_INTENSITY] = 3

    assert gismeteo.condition(data) == ATTR_CONDITION_POURING
    assert gismeteo_d.condition(data) == ATTR_CONDITION_POURING

    data[ATTR_FORECAST_PRECIPITATION_TYPE] = 3

    assert gismeteo.condition(data) == ATTR_CONDITION_SNOWY_RAINY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_SNOWY_RAINY

    data[ATTR_FORECAST_PRECIPITATION_TYPE] = 0
    data[ATTR_FORECAST_NATIVE_WIND_SPEED] = 11

    assert gismeteo.condition(data) == ATTR_CONDITION_WINDY_VARIANT
    assert gismeteo_d.condition(data) == ATTR_CONDITION_WINDY_VARIANT

    data[ATTR_FORECAST_CLOUD_COVERAGE] = 0

    assert gismeteo.condition(data) == ATTR_CONDITION_WINDY
    assert gismeteo_d.condition(data) == ATTR_CONDITION_WINDY

    data[ATTR_FORECAST_NATIVE_WIND_SPEED] = 0

    for cnd in CONDITION_FOG_CLASSES:
        data[ATTR_FORECAST_PHENOMENON] = cnd

        assert gismeteo.condition(data) == ATTR_CONDITION_FOG
        assert gismeteo_d.condition(data) == ATTR_CONDITION_FOG


async def test_temperature():
    """Test temperature."""
    gismeteo = await init_gismeteo()

    assert gismeteo.temperature() == -7.0
    assert gismeteo.temperature(gismeteo.current_data) == -7.0

    assert gismeteo.temperature(gismeteo.forecast_data(0)) == -7.0
    assert gismeteo.temperature(gismeteo.forecast_data(3)) == -11.0


async def test_apparent_temperature():
    """Test apparent temperature feels like."""
    gismeteo = await init_gismeteo()

    assert gismeteo.apparent_temperature() == -12.3
    assert gismeteo.apparent_temperature(gismeteo.current_data) == -12.3

    assert gismeteo.apparent_temperature(gismeteo.forecast_data(0)) == -12.3
    assert gismeteo.apparent_temperature(gismeteo.forecast_data(3)) == -17.2

    for stype in ["temperature", "humidity", "wind_speed"]:
        with patch.object(gismeteo, stype, return_value=None):
            assert gismeteo.apparent_temperature() is None


async def test_water_temperature():
    """Test temperature of water."""
    gismeteo = await init_gismeteo()

    assert gismeteo.water_temperature() == 3.0
    assert gismeteo.water_temperature(gismeteo.current_data) == 3.0

    assert gismeteo.water_temperature(gismeteo.forecast_data(0)) == STATE_UNKNOWN
    assert gismeteo.water_temperature(gismeteo.forecast_data(3)) == STATE_UNKNOWN


async def test_pressure():
    """Test pressure in hPa."""
    gismeteo = await init_gismeteo()

    assert gismeteo.pressure() == 746
    assert gismeteo.pressure(gismeteo.current_data) == 746

    assert gismeteo.pressure(gismeteo.forecast_data(0)) == 746
    assert gismeteo.pressure(gismeteo.forecast_data(3)) == 749


async def test_humidity():
    """Test humidity."""
    gismeteo = await init_gismeteo()

    assert gismeteo.humidity() == 86
    assert gismeteo.humidity(gismeteo.current_data) == 86

    assert gismeteo.humidity(gismeteo.forecast_data(0)) == 86
    assert gismeteo.humidity(gismeteo.forecast_data(3)) == 89


async def test_wind_bearing():
    """Test wind bearing."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_bearing() == 180
    assert gismeteo.wind_bearing(gismeteo.current_data) == 180

    assert gismeteo.wind_bearing(gismeteo.forecast_data(0)) == 180
    assert gismeteo.wind_bearing(gismeteo.forecast_data(3)) == 45


async def test_wind_bearing_label():
    """Test wind bearing labels."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_bearing_label() == "s"
    assert gismeteo.wind_bearing_label(gismeteo.current_data) == "s"

    assert gismeteo.wind_bearing_label(gismeteo.forecast_data(0)) == "s"
    assert gismeteo.wind_bearing_label(gismeteo.forecast_data(3)) == "ne"


async def test_wind_gust_speed():
    """Test wind gust speed in m/s."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_gust_speed() is None
    assert gismeteo.wind_gust_speed(gismeteo.current_data) is None

    assert gismeteo.wind_gust_speed(gismeteo.forecast_data(0)) is None
    assert gismeteo.wind_gust_speed(gismeteo.forecast_data(3)) == 4


async def test_wind_speed():
    """Test wind speed in m/s."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_speed() == 3.0
    assert gismeteo.wind_speed(gismeteo.current_data) == 3.0

    assert gismeteo.wind_speed(gismeteo.forecast_data(0)) == 3.0
    assert gismeteo.wind_speed(gismeteo.forecast_data(3)) == 4.0


async def test_precipitation_type():
    """Test precipitation type."""
    gismeteo = await init_gismeteo()

    assert gismeteo.precipitation_type() == "snow"
    assert gismeteo.precipitation_type(gismeteo.current_data) == "snow"

    assert gismeteo.precipitation_type(gismeteo.forecast_data(0)) == "snow"
    assert gismeteo.precipitation_type(gismeteo.forecast_data(3)) == "snow"


async def test_precipitation_amount():
    """Test precipitation amount."""
    gismeteo = await init_gismeteo()

    assert gismeteo.precipitation_amount() == 0.3
    assert gismeteo.precipitation_amount(gismeteo.current_data) == 0.3

    assert gismeteo.precipitation_amount(gismeteo.forecast_data(0)) == 2.2
    assert gismeteo.precipitation_amount(gismeteo.forecast_data(3)) == 0.1


async def test_precipitation_intensity():
    """Test precipitation intensity."""
    gismeteo = await init_gismeteo()

    assert gismeteo.precipitation_intensity() == "small"
    assert gismeteo.precipitation_intensity(gismeteo.current_data) == "small"

    assert gismeteo.precipitation_intensity(gismeteo.forecast_data(0)) == "heavy"
    assert gismeteo.precipitation_intensity(gismeteo.forecast_data(3)) == "small"


async def test_cloud_coverage():
    """Test the cloudiness amount in percents."""
    gismeteo = await init_gismeteo()

    assert gismeteo.cloud_coverage() == 100
    assert gismeteo.cloud_coverage(gismeteo.current_data) == 100

    assert gismeteo.cloud_coverage(gismeteo.forecast_data(0)) == 100
    assert gismeteo.cloud_coverage(gismeteo.forecast_data(3)) == 100


async def test_rain_amount():
    """Test the rain amount in mm."""
    gismeteo = await init_gismeteo()

    assert gismeteo.rain_amount() == 0
    assert gismeteo.rain_amount(gismeteo.current_data) == 0

    assert gismeteo.rain_amount(gismeteo.forecast_data(0)) == 0
    assert gismeteo.rain_amount(gismeteo.forecast_data(3)) == 0


async def test_snow_amount():
    """Test the snow amount in mm."""
    gismeteo = await init_gismeteo()

    assert gismeteo.snow_amount() == 0.3
    assert gismeteo.snow_amount(gismeteo.current_data) == 0.3

    assert gismeteo.snow_amount(gismeteo.forecast_data(0)) == 2.2
    assert gismeteo.snow_amount(gismeteo.forecast_data(3)) == 0.1


async def test_is_storm():
    """Test storm prediction."""
    gismeteo = await init_gismeteo()

    assert gismeteo.is_storm() is False
    assert gismeteo.is_storm(gismeteo.current_data) is False

    assert gismeteo.is_storm(gismeteo.forecast_data(0)) is False
    assert gismeteo.is_storm(gismeteo.forecast_data(3)) is False


async def test_geomagnetic_field():
    """Test geomagnetic field index."""
    gismeteo = await init_gismeteo()

    assert gismeteo.geomagnetic_field() == 3
    assert gismeteo.geomagnetic_field(gismeteo.current_data) == 3

    assert gismeteo.geomagnetic_field(gismeteo.forecast_data(0)) == 3
    assert gismeteo.geomagnetic_field(gismeteo.forecast_data(3)) == 3


async def test_pollen_birch():
    """Test birch pollen value."""
    gismeteo_d = await init_gismeteo()

    assert gismeteo_d.pollen_birch() == 2

    for day, exp in enumerate([2, 2, 2, 1, 1, 3, 2]):
        assert (
            gismeteo_d.pollen_birch(gismeteo_d.forecast_data(day, FORECAST_MODE_DAILY))
            == exp
        )


async def test_pollen_grass():
    """Test grass pollen value."""
    gismeteo_d = await init_gismeteo()

    assert gismeteo_d.pollen_grass() is None

    for day, exp in enumerate([None, None, None, None, None, None, None]):
        assert (
            gismeteo_d.pollen_grass(gismeteo_d.forecast_data(day, FORECAST_MODE_DAILY))
            == exp
        )


async def test_pollen_ragweed():
    """Test ragweed pollen value."""
    gismeteo_d = await init_gismeteo()

    assert gismeteo_d.pollen_ragweed() is None

    for day, exp in enumerate([None, None, None, None, None, None, None]):
        assert (
            gismeteo_d.pollen_ragweed(
                gismeteo_d.forecast_data(day, FORECAST_MODE_DAILY)
            )
            == exp
        )


async def test_uv_index():
    """Test UV index."""
    gismeteo_d = await init_gismeteo()

    assert gismeteo_d.uv_index() == 2

    for day, exp in enumerate([2, 4, 3, 5, 7, 1, 7]):
        assert (
            gismeteo_d.uv_index(gismeteo_d.forecast_data(day, FORECAST_MODE_DAILY))
            == exp
        )


async def test_road_condition():
    """Test road condition."""
    gismeteo_d = await init_gismeteo()

    assert gismeteo_d.road_condition() == "dry"

    for day, exp in enumerate(["dry", "dry", "dry", "dry", None, None, None]):
        assert (
            gismeteo_d.road_condition(
                gismeteo_d.forecast_data(day, FORECAST_MODE_DAILY)
            )
            == exp
        )


#
# async def test_forecast():
#     """Test forecast."""
#     with patch(
#         "homeassistant.util.dt.now",
#         return_value=datetime(2021, 2, 26, tzinfo=dt_util.UTC),
#     ):
#         gismeteo_d = await init_gismeteo()
#
#         assert gismeteo_d.forecast(FORECAST_MODE_DAILY) == [
#             {
#                 "datetime": datetime(2021, 2, 26, tzinfo=TZ180),
#                 "condition": "rainy",
#                 "temperature": 4.0,
#                 "pressure": 0.0,
#                 "humidity": 89,
#                 "wind_speed": 7,
#                 "wind_bearing": 270,
#                 "precipitation": 0.3,
#                 "templow": 2,
#             },
#             {
#                 "datetime": datetime(2021, 2, 27, tzinfo=TZ180),
#                 "condition": "cloudy",
#                 "temperature": 2.0,
#                 "pressure": 0.0,
#                 "humidity": 87,
#                 "wind_speed": 6,
#                 "wind_bearing": 270,
#                 "precipitation": 0.0,
#                 "templow": 0,
#             },
#         ]
