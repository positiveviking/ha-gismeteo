*Please :star: this repo if you find it useful*

# Gismeteo Weather Provider for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Support me on Patreon][patreon-shield]][patreon]

[![Community Forum][forum-shield]][forum]

_Component to integrate with Gismeteo weather provider._

This component can be used in two different ways: as a weather provider and as a set of sensors.

![Gismeteo Logo][exampleimg]

*NB. You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).*

I also suggest you [visit the support topic][forum] on the community forum.

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Gismeteo Weather Provider".
1. Click Install below the found integration.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gismeteo".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `gismeteo`.
1. Download file `gismeteo.zip` from the [latest release section][latest-release] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) `gismeteo` you created.
1. Restart Home Assistant
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gismeteo".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

## Breaking Changes

- Since version 3.0.0...
    - the format of the component settings in file `configuration.yaml` has been changed. Now all the component settings are collected in a single block `gismeteo`.
    - forecast sensor is removed from component. Use `forecast_days` option instead.
- Since version 2.2.0 forecast sensor has the name `... 3h Forecast` instead of `... Forecast`.

## Configuration Examples

Adding the following to your `configuration.yaml` file will create two weather locations,
one for the home coordinates and one for the remote location.

The first location will create one entity: just weather provider. The second location will create 21
sensors: four groups of sensors for current weather and forecasts for today and 2 days forward.
Another 78 sensors will be created but disabled. You can enable that sensors through device settings.
```yaml
# Example configuration.yaml entry
gismeteo:
  sweet_home:

  dacha:
    name: Our Country House
    latitude: ...
    longitude: ...
    add_sensors: yes
    forecast_days: 2
```

See below detailed descriptions to configure component.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

## Configuration variables

**gismeteo:**\
  _(map) (**Required**)_\
  Map of your weather locations.

> **name:**\
>   _(string) (Optional)_\
>   Name to use in the frontend.
>
> **latitude:**\
>   _(float) (Optional) (Default: coordinates from the Home Assistant configuration)_\
>   Latitude coordinate to monitor weather of (required if `longitude` is specified).
>
> **longitude:**\
>   _(float) (Optional) (Default: coordinates from the Home Assistant configuration)_\
>   Longitude coordinate to monitor weather of (required if `latitude` is specified).
>
> **add_sensors:**\
>   _(boolean) (Optional) (Default: false)_\
>   Enable this option to add current weather and forecast sensors to the frontend.
>
> **forecast_days:**\
>   _(positive int; 0–6) (Optional) (Default: do not create any sensors)_\
>   How many days ahead to make forecast sensors.\
>   **Note:** Forecast sensors will be created only if `add_sensors` option is enabled.\
>   **Note:** If you only need a forecast sensors for today, specify `0`.

When `sensors` option are enabled, it creates 20 sensors. Each shows one aspect of current weather. Only few basic sensors are enabled by default. But you can enable any sensor through device settings.

When you add `forecast_days` option, integration creates additional 21 sensors for each day. Each shows one aspect of forecast weather for that day. As usual, only few basic sensors are enabled by default.

List of sensors that will be created:
> **condition**\
>   A human-readable text summary.
>
> **temperature**\
>   The air temperature.
>
> **apparent_temperature**\
>   The apparent air temperature.
>
> **low_temperature**\
>   The lowest air temperature per day.
>
> **humidity**\
>   The relative humidity of air.
>
> **pressure**\
>   The sea-level air pressure.
>
> **wind_speed**\
>   The wind speed.
>
> **wind_gusts_speed**\
>   The wind gusts speed.
>
> **wind_bearing**\
>   The wind bearing as an angle.
>
> **wind_bearing_2**\
>   The wind bearing as human-readable text.
>
> **cloud_coverage**\
>   Cloud coverage as a percentage.
>
> **precipitation**\
>   The precipitation amount volume.
>
> **rain_amount**\
>   The rain amount volume.
>
> **snow_amount**\
>   The snow amount volume.
>
> **storm**\
>   The storm prediction.
>
> **geomagnetic_field**\
>   The geomagnetic field value:\
>   1 = No noticeable geomagnetic disturbance\
>   2 = Small geomagnetic disturbances\
>   3 = Weak geomagnetic storm\
>   4 = Small geomagnetic storm\
>   5 = Moderate geomagnetic storm\
>   6 = Severe geomagnetic storm\
>   7 = Hard geomagnetic storm\
>   8 = Extreme geomagnetic storm
>
> **water_temperature**\
>   The temperature of water.
>
> **uv_index**\
>   The ultraviolet index:\
>   0–2 = Low\
>   3–5 = Moderate\
>   6–7 = High\
>   8–10 = Very high\
>   11+ = Extreme
>
> **birch_pollen**\
>   Birch pollen concentration index:\
>   1–10 = Low\
>   11–50 = Moderate\
>   51–500 = High\
>   501+ = Very high
>
> **grass_pollen**\
>   Cereal grasses pollen concentration index:\
>   1–10 = Low\
>   11–50 = Moderate\
>   51–500 = High\
>   501+ = Very high
>
> **ragweed_pollen**\
>   Ragweed pollen concentration index:\
>   1–10 = Low\
>   11–50 = Moderate\
>   51–500 = High\
>   501+ = Very high
>
> **road_condition**\
>   Road surface condition as a human-readable text.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.gismeteo: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-gismeteo
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-gismeteo.svg?style=popout
[commits]: https://github.com/Limych/ha-gismeteo/commits/dev
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-gismeteo/raw/dev/gismeteo_logo.jpg
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/gismeteo-weather-provider/109668
[license]: https://github.com/Limych/ha-gismeteo/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-gismeteo.svg?style=popout
[releases]: https://github.com/Limych/ha-gismeteo/releases
[releases-latest]: https://github.com/Limych/ha-gismeteo/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-gismeteo/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-gismeteo/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-gismeteo/graphs/contributors
[patreon-shield]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DLimych%26type%3Dpatrons&style=popout
[patreon]: https://www.patreon.com/join/limych
