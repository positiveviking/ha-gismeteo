#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from http import HTTPStatus
import logging
import math
from typing import Any
import xml.etree.ElementTree as etree  # type: ignore

from aiohttp import ClientSession
from bs4 import BeautifulSoup

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
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.const import ATTR_ID, ATTR_LATITUDE, ATTR_LONGITUDE, STATE_UNKNOWN
from homeassistant.util import Throttle, dt as dt_util

from .cache import Cache
from .const import (
    ATTR_FORECAST_CLOUDINESS,
    ATTR_FORECAST_GEOMAGNETIC_FIELD,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_PRECIPITATION_AMOUNT,
    ATTR_FORECAST_PRECIPITATION_INTENSITY,
    ATTR_FORECAST_PRECIPITATION_TYPE,
    ATTR_FORECAST_PRESSURE,
    ATTR_FORECAST_STORM,
    ATTR_SUNRISE,
    ATTR_SUNSET,
    ATTR_WEATHER_ALLERGY_BIRCH,
    ATTR_WEATHER_CLOUDINESS,
    ATTR_WEATHER_CONDITION,
    ATTR_WEATHER_GEOMAGNETIC_FIELD,
    ATTR_WEATHER_PHENOMENON,
    ATTR_WEATHER_PRECIPITATION_AMOUNT,
    ATTR_WEATHER_PRECIPITATION_INTENSITY,
    ATTR_WEATHER_PRECIPITATION_TYPE,
    ATTR_WEATHER_STORM,
    ATTR_WEATHER_UV_INDEX,
    ATTR_WEATHER_WATER_TEMPERATURE,
    CONDITION_FOG_CLASSES,
    ENDPOINT_URL,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    MMHG2HPA,
    MS2KMH,
    PARSED_UPDATE_INTERVAL,
    PARSER_URL_FORMAT,
    PARSER_USER_AGENT,
    PRECIPITATION_AMOUNT,
)

_LOGGER = logging.getLogger(__name__)


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are invalid."""

    def __init__(self, status):
        """Initialize."""
        super().__init__(status)
        self.status = status


class ApiError(Exception):
    """Raised when Gismeteo API request ended in error."""

    def __init__(self, status):
        """Initialize."""
        super().__init__(status)
        self.status = status


class GismeteoApiClient:
    """Gismeteo API implementation."""

    def __init__(
        self,
        session: ClientSession,
        location_key: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        params: dict | None = None,
    ):
        """Initialize."""
        params = params or {}

        self._session = session
        self._cache = Cache(params) if params.get("cache_dir") is not None else None
        self._attributes = {}

        if location_key is not None:
            _LOGGER.debug("Place location ID: %s", location_key)
            self._attributes = {
                ATTR_ID: location_key,
            }
        elif self._valid_coordinates(latitude, longitude):
            _LOGGER.debug("Place coordinates: %s, %s", latitude, longitude)
            self._attributes = {
                ATTR_LATITUDE: latitude,
                ATTR_LONGITUDE: longitude,
            }
        else:
            raise InvalidCoordinatesError("Your coordinates are invalid.")

        self._current = {}
        self._forecast_hourly = []
        self._forecast_daily = []
        self._parsed = {}

    @staticmethod
    def _valid_coordinates(latitude: float, longitude: float) -> bool:
        """Return True if coordinates are valid."""
        try:
            assert isinstance(latitude, int | float) and isinstance(
                longitude, int | float
            )
            assert abs(latitude) <= 90 and abs(longitude) <= 180
        except (AssertionError, TypeError):
            return False
        return True

    @property
    def attributes(self):
        """Return an attributes."""
        return self._attributes

    @property
    def current_data(self):
        """Return current weather data."""
        return self._current

    def forecast_data(self, pos: int, mode: str = FORECAST_MODE_HOURLY):
        """Return forecast data."""
        forecast = []
        now = dt_util.now()
        for data in (
            self._forecast_hourly
            if mode == FORECAST_MODE_HOURLY
            else self._forecast_daily
        ):
            fc_time = data.get(ATTR_FORECAST_TIME)
            if fc_time is None:
                continue  # pragma: no cover

            if fc_time < now:
                forecast = [data]
            else:
                forecast.append(data)

        try:
            return forecast[pos]

        except IndexError:
            return {}

    async def _async_get_data(
        self, url: str, cache_fname: str | None = None, as_browser: bool = False
    ) -> str:
        """Retreive data from Gismeteo API and cache results."""
        _LOGGER.debug("Requesting URL %s", url)

        if self._cache and cache_fname is not None:
            cache_fname += ".xml"
            if self._cache.is_cached(cache_fname):
                _LOGGER.debug("Cached response used")
                return self._cache.read_cache(cache_fname)

        headers = {}
        if as_browser:
            headers["User-Agent"] = PARSER_USER_AGENT

        async with self._session.get(url, headers=headers) as resp:
            if resp.status != HTTPStatus.OK:
                raise ApiError(f"Invalid response from Gismeteo API: {resp.status}")
            _LOGGER.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.text()

        if self._cache and cache_fname is not None and data:
            self._cache.save_cache(cache_fname, data)

        return data

    async def async_update_location(self):
        """Retreive location data from Gismeteo."""
        url = (
            ENDPOINT_URL
            + f"/cities/?lat={self._attributes[ATTR_LATITUDE]}&lng={self._attributes[ATTR_LONGITUDE]}&count=1&lang=en"
        )
        cache_fname = f"location_{self._attributes[ATTR_LATITUDE]}_{self._attributes[ATTR_LONGITUDE]}"

        response = await self._async_get_data(url, cache_fname)
        try:
            xml = etree.fromstring(response)
            item = xml.find("item")
            self._attributes = {
                ATTR_ID: self._get(item, "id", int),
                ATTR_LATITUDE: self._get(item, "lat", float),
                ATTR_LONGITUDE: self._get(item, "lng", float),
            }

        except (etree.ParseError, TypeError, AttributeError) as ex:
            raise ApiError(
                "Can't retrieve location data! Invalid server response."
            ) from ex

    async def async_get_forecast(self):
        """Get the latest forecast data from Gismeteo."""
        if ATTR_ID not in self.attributes:
            await self.async_update_location()

        url = f"{ENDPOINT_URL}/forecast/?city={self.attributes[ATTR_ID]}&lang=en"
        cache_fname = f"forecast_{self.attributes[ATTR_ID]}"

        return await self._async_get_data(url, cache_fname)

    async def async_get_parsed(self):
        """Retrieve data from Gismeteo main site."""
        forecast = await self.async_get_forecast()
        location = etree.fromstring(forecast).find("location")
        location_uri = str(location.get("nowcast_url")).strip("/")[8:]
        tzone = int(location.get("tzone"))
        today = self._get_utime(location.get("cur_time")[:10], tzone)

        data = {}
        url = PARSER_URL_FORMAT.format(location_uri)
        cache_fname = f"forecast_parsed_{self.attributes[ATTR_ID]}"

        response = await self._async_get_data(url, cache_fname, as_browser=True)

        parser = BeautifulSoup(response, "html.parser")

        try:
            for key in ("allergy", "uvb"):
                data_div = parser.find("div", {"data-widget-id": key})
                for item in data_div.find_all("div", {"class": "widget__item"}):
                    day = int(item.attrs["data-item"])
                    date = today + timedelta(days=day)
                    value = item.find("div", {"class": "widget__value"})
                    if value:
                        data.setdefault(date, {})
                        data[date][key] = int(value.text.strip())

            return data

        except AttributeError:  # pragma: no cover
            return {}

    @staticmethod
    def _get(var: dict, ind: str, func: Callable | None = None) -> Any:
        res = var.get(ind)
        if func is not None:
            try:
                res = func(res)
            except (TypeError, ValueError, ArithmeticError):
                return None
        return res

    @staticmethod
    def _is_day(testing_time: datetime, sunrise_time: datetime, sunset_time: datetime):
        """Return True if sun are shining."""
        return sunrise_time < testing_time < sunset_time

    def condition(self, src=None, mode: str = FORECAST_MODE_HOURLY):
        """Return the condition summary."""
        src = src or self._current

        cld = src.get(ATTR_WEATHER_CLOUDINESS)
        if cld is None:
            return None
        if cld == 0:
            if mode == FORECAST_MODE_DAILY or self._is_day(
                src.get(ATTR_FORECAST_TIME, dt_util.now()),
                src.get(ATTR_SUNRISE),
                src.get(ATTR_SUNSET),
            ):
                cond = ATTR_CONDITION_SUNNY  # Sunshine
            else:
                cond = ATTR_CONDITION_CLEAR_NIGHT  # Clear night
        elif cld == 1:
            cond = ATTR_CONDITION_PARTLYCLOUDY  # A few clouds
        elif cld == 2:
            cond = ATTR_CONDITION_PARTLYCLOUDY  # A some clouds
        else:
            cond = ATTR_CONDITION_CLOUDY  # Many clouds

        pr_type = src.get(ATTR_WEATHER_PRECIPITATION_TYPE)
        pr_int = src.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
        if src.get(ATTR_WEATHER_STORM):
            cond = ATTR_CONDITION_LIGHTNING  # Lightning/ thunderstorms
            if pr_type != 0:
                cond = (
                    ATTR_CONDITION_LIGHTNING_RAINY  # Lightning/ thunderstorms and rain
                )
        elif pr_type == 1:
            cond = ATTR_CONDITION_RAINY  # Rain
            if pr_int == 3:
                cond = ATTR_CONDITION_POURING  # Pouring rain
        elif pr_type == 2:
            cond = ATTR_CONDITION_SNOWY  # Snow
        elif pr_type == 3:
            cond = ATTR_CONDITION_SNOWY_RAINY  # Snow and Rain
        elif self.wind_speed(src) > 10.8:
            if cond == ATTR_CONDITION_CLOUDY:
                cond = ATTR_CONDITION_WINDY_VARIANT  # Wind and clouds
            else:
                cond = ATTR_CONDITION_WINDY  # Wind
        elif (
            cld == 0
            and src.get(ATTR_WEATHER_PHENOMENON) is not None
            and src.get(ATTR_WEATHER_PHENOMENON) in CONDITION_FOG_CLASSES
        ):
            cond = ATTR_CONDITION_FOG  # Fog

        return cond

    def temperature(self, src=None):
        """Return the temperature."""
        src = src or self._current
        temperature = src.get(ATTR_WEATHER_TEMPERATURE)
        return float(temperature) if temperature is not None else STATE_UNKNOWN

    def temperature_feels_like(self, src=None):
        """Return the temperature feels like."""
        temp = self.temperature(src)
        humi = self.humidity(src)
        wind = self.wind_speed(src)
        if STATE_UNKNOWN in (temp, humi, wind):
            return STATE_UNKNOWN

        e_value = humi * 0.06105 * math.exp((17.27 * temp) / (237.7 + temp))
        feels = temp + 0.348 * e_value - 0.7 * wind - 4.25
        return round(feels, 1)

    def water_temperature(self, src=None):
        """Return the temperature of water."""
        src = src or self._current
        temperature = src.get(ATTR_WEATHER_WATER_TEMPERATURE)
        return float(temperature) if temperature is not None else STATE_UNKNOWN

    def pressure(self, src=None):
        """Return the pressure in hPa."""
        src = src or self._current
        pressure = src.get(ATTR_WEATHER_PRESSURE)
        return round(pressure * MMHG2HPA, 1) if pressure is not None else STATE_UNKNOWN

    def humidity(self, src=None):
        """Return the humidity."""
        src = src or self._current
        humidity = src.get(ATTR_WEATHER_HUMIDITY)
        return int(humidity) if humidity is not None else STATE_UNKNOWN

    def wind_bearing(self, src=None):
        """Return the wind bearing."""
        src = src or self._current
        bearing = int(src.get(ATTR_WEATHER_WIND_BEARING, 0))
        return (bearing - 1) * 45 if bearing > 0 else STATE_UNKNOWN

    def wind_speed_kmh(self, src=None):
        """Return the wind speed in km/h."""
        src = src or self._current
        speed = src.get(ATTR_WEATHER_WIND_SPEED)
        return round(speed * MS2KMH, 1) if speed is not None else STATE_UNKNOWN

    def wind_speed(self, src=None):
        """Return the wind speed in m/s."""
        src = src or self._current
        speed = src.get(ATTR_WEATHER_WIND_SPEED)
        return float(speed) if speed is not None else STATE_UNKNOWN

    def precipitation_amount(self, src=None):
        """Return the precipitation amount in mm."""
        src = src or self._current
        precipitation = src.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
        return precipitation if precipitation is not None else STATE_UNKNOWN

    def clouds(self, src=None):
        """Return the cloudiness amount in percents."""
        src = src or self._current
        cloudiness = src.get(ATTR_WEATHER_CLOUDINESS)
        return int(cloudiness * 100 / 3) if cloudiness is not None else STATE_UNKNOWN

    def rain(self, src=None):
        """Return the rain amount in mm."""
        src = src or self._current
        return (
            (
                src.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                or PRECIPITATION_AMOUNT[src.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)]
            )
            if src.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [1, 3]
            else 0
        )

    def snow(self, src=None):
        """Return the snow amount in mm."""
        src = src or self._current
        return (
            (
                src.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                or PRECIPITATION_AMOUNT[src.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)]
            )
            if src.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [2, 3]
            else 0
        )

    def storm(self, src=None):
        """Return True if storm."""
        src = src or self._current
        storm = src.get(ATTR_WEATHER_STORM)
        return storm if storm is not None else STATE_UNKNOWN

    def geomagnetic(self, src=None):
        """Return geomagnetic field index."""
        src = src or self._current
        geomagnetic = src.get(ATTR_WEATHER_GEOMAGNETIC_FIELD)
        return geomagnetic if geomagnetic is not None else STATE_UNKNOWN

    def allergy_birch(self, src=None):
        """Return allergy birch value."""
        src = src or self.forecast_data(0, FORECAST_MODE_DAILY)
        allergy = src.get(ATTR_WEATHER_ALLERGY_BIRCH)
        return allergy if allergy is not None else STATE_UNKNOWN

    def uv_index(self, src=None):
        """Return UV index."""
        src = src or self.forecast_data(0, FORECAST_MODE_DAILY)
        uv_index = src.get(ATTR_WEATHER_UV_INDEX)
        return uv_index if uv_index is not None else STATE_UNKNOWN

    def forecast(self, mode: str = FORECAST_MODE_HOURLY):
        """Return the forecast array."""
        now = dt_util.now()
        forecast = []
        for i in (
            self._forecast_hourly
            if mode == FORECAST_MODE_HOURLY
            else self._forecast_daily
        ):
            fc_time = i.get(ATTR_FORECAST_TIME)
            if fc_time is None:
                continue  # pragma: no cover

            data = {
                ATTR_FORECAST_TIME: fc_time,
                ATTR_FORECAST_CONDITION: self.condition(i, mode),
                ATTR_FORECAST_TEMP: self.temperature(i),
                ATTR_FORECAST_PRESSURE: self.pressure(i),
                ATTR_FORECAST_HUMIDITY: self.humidity(i),
                ATTR_FORECAST_WIND_SPEED: self.wind_speed_kmh(i),
                ATTR_FORECAST_WIND_BEARING: self.wind_bearing(i),
                ATTR_FORECAST_PRECIPITATION: self.precipitation_amount(i),
            }

            if (
                mode == FORECAST_MODE_DAILY
                and i.get(ATTR_FORECAST_TEMP_LOW) is not None
            ):
                data[ATTR_FORECAST_TEMP_LOW] = i.get(ATTR_FORECAST_TEMP_LOW)

            if fc_time < now:
                forecast = [data]
            else:
                forecast.append(data)

        return forecast

    @staticmethod
    def _get_utime(source: str, tzone: int) -> datetime:
        """Get local datetime for given datetime as string.

        :raise ValueError
        """
        local_date = source
        if len(source) <= 10:
            local_date += "T00:00:00"
        tz_h, tz_m = divmod(abs(tzone), 60)
        local_date += f"+{tz_h:02}:{tz_m:02}" if tzone >= 0 else f"-{tz_h:02}:{tz_m:02}"
        return dt_util.parse_datetime(local_date, raise_on_error=True)

    @Throttle(PARSED_UPDATE_INTERVAL)
    async def async_update_parsed(self):
        """Update parsed data."""
        self._parsed = await self.async_get_parsed()

    async def async_update(self) -> bool:
        """Get the latest data from Gismeteo."""
        response = await self.async_get_forecast()
        try:
            xml = etree.fromstring(response)
            current = xml.find("location/fact")
            current_v = current.find("values")
            tzone = int(xml.find("location").get("tzone"))
            today = self._get_utime(current.get("valid"), tzone)

            await self.async_update_parsed()

            self._current = {
                ATTR_SUNRISE: datetime.fromtimestamp(
                    self._get(current, "sunrise", int), today.tzinfo
                ),
                ATTR_SUNSET: datetime.fromtimestamp(
                    self._get(current, "sunset", int), today.tzinfo
                ),
                ATTR_WEATHER_CONDITION: self._get(current_v, "descr"),
                ATTR_WEATHER_TEMPERATURE: self._get(current_v, "tflt", float),
                ATTR_WEATHER_PRESSURE: self._get(current_v, "p", int),
                ATTR_WEATHER_HUMIDITY: self._get(current_v, "hum", int),
                ATTR_WEATHER_WIND_SPEED: self._get(current_v, "ws", int),
                ATTR_WEATHER_WIND_BEARING: self._get(current_v, "wd", int),
                ATTR_WEATHER_CLOUDINESS: self._get(current_v, "cl", int),
                ATTR_WEATHER_PRECIPITATION_TYPE: self._get(current_v, "pt", int),
                ATTR_WEATHER_PRECIPITATION_AMOUNT: self._get(current_v, "prflt", float),
                ATTR_WEATHER_PRECIPITATION_INTENSITY: self._get(current_v, "pr", int),
                ATTR_WEATHER_STORM: (self._get(current_v, "ts") == 1),
                ATTR_WEATHER_GEOMAGNETIC_FIELD: self._get(current_v, "grade", int),
                ATTR_WEATHER_PHENOMENON: self._get(current_v, "ph", int),
                ATTR_WEATHER_WATER_TEMPERATURE: self._get(current_v, "water_t", float),
            }

            # Update hourly forecast
            self._forecast_hourly = []
            for day in xml.findall("location/day"):
                sunrise = datetime.fromtimestamp(
                    self._get(day, "sunrise", int), today.tzinfo
                )
                sunset = datetime.fromtimestamp(
                    self._get(day, "sunset", int), today.tzinfo
                )

                for i in day.findall("forecast"):
                    fc_v = i.find("values")
                    tstamp = self._get_utime(i.get("valid"), tzone)
                    tstamp_day = self._get_utime(i.get("valid")[:10], tzone)
                    data = {
                        ATTR_SUNRISE: sunrise,
                        ATTR_SUNSET: sunset,
                        ATTR_FORECAST_TIME: tstamp,
                        ATTR_FORECAST_CONDITION: self._get(fc_v, "descr"),
                        ATTR_FORECAST_TEMP: self._get(fc_v, "t", int),
                        ATTR_FORECAST_PRESSURE: self._get(fc_v, "p", int),
                        ATTR_FORECAST_HUMIDITY: self._get(fc_v, "hum", int),
                        ATTR_FORECAST_WIND_SPEED: self._get(fc_v, "ws", int),
                        ATTR_FORECAST_WIND_BEARING: self._get(fc_v, "wd", int),
                        ATTR_FORECAST_CLOUDINESS: self._get(fc_v, "cl", int),
                        ATTR_FORECAST_PRECIPITATION_TYPE: self._get(fc_v, "pt", int),
                        ATTR_FORECAST_PRECIPITATION_AMOUNT: self._get(
                            fc_v, "prflt", float
                        ),
                        ATTR_FORECAST_PRECIPITATION_INTENSITY: self._get(
                            fc_v, "pr", int
                        ),
                        ATTR_FORECAST_STORM: (fc_v.get("ts") == 1),
                        ATTR_FORECAST_GEOMAGNETIC_FIELD: self._get(fc_v, "grade", int),
                    }

                    parsed = self._parsed.get(tstamp_day)
                    if parsed:
                        data.update(
                            {
                                ATTR_WEATHER_ALLERGY_BIRCH: self._get(
                                    parsed, "allergy"
                                ),
                                ATTR_WEATHER_UV_INDEX: self._get(parsed, "uvb"),
                            }
                        )

                    self._forecast_hourly.append(data)

            # Update daily forecast
            self._forecast_daily = []
            for day in xml.findall("location/day[@descr]"):
                tstamp = self._get_utime(day.get("date"), tzone)
                data = {
                    ATTR_SUNRISE: self._get(day, "sunrise", int),
                    ATTR_SUNSET: self._get(day, "sunset", int),
                    ATTR_FORECAST_TIME: tstamp,
                    ATTR_FORECAST_CONDITION: self._get(day, "descr"),
                    ATTR_FORECAST_TEMP: self._get(day, "tmax", int),
                    ATTR_FORECAST_TEMP_LOW: self._get(day, "tmin", int),
                    ATTR_FORECAST_PRESSURE: self._get(day, "p", int),
                    ATTR_FORECAST_HUMIDITY: self._get(day, "hum", int),
                    ATTR_FORECAST_WIND_SPEED: self._get(day, "ws", int),
                    ATTR_FORECAST_WIND_BEARING: self._get(day, "wd", int),
                    ATTR_FORECAST_CLOUDINESS: self._get(day, "cl", int),
                    ATTR_FORECAST_PRECIPITATION_TYPE: self._get(day, "pt", int),
                    ATTR_FORECAST_PRECIPITATION_AMOUNT: self._get(day, "prflt", float),
                    ATTR_FORECAST_PRECIPITATION_INTENSITY: self._get(day, "pr", int),
                    ATTR_FORECAST_STORM: (self._get(day, "ts") == 1),
                    ATTR_FORECAST_GEOMAGNETIC_FIELD: self._get(day, "grademax", int),
                }

                parsed = self._parsed.get(tstamp)
                if parsed:
                    data.update(
                        {
                            ATTR_WEATHER_ALLERGY_BIRCH: self._get(parsed, "allergy"),
                            ATTR_WEATHER_UV_INDEX: self._get(parsed, "uvb"),
                        }
                    )

                self._forecast_daily.append(data)

            return True

        except (etree.ParseError, TypeError, AttributeError) as ex:
            raise ApiError(
                "Can't update weather data! Invalid server response."
            ) from ex
