**New as of Version 0.5.0!** Trigger your automations with the `nhl_goal` event platform. See the [example automations](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md) for more information.

## Information:
Track the score of your favorite NHL team and create automations based on your team scoring!

<span style="color:red">*New!*</span> The sensor will only fetch data every 10 minutes when the game is not live and will then update at the user defined frequency (or every second if undefined) once the game is live.

## Usage:
Add to configuration.yaml:

```
sensor:
  - platform: nhl_api
    team_id: [TEAM ID OF TRACKED TEAM - REFER TO DOCS]
    name: [(Optional) FRIENDLY NAME OF SENSOR - DEFAULT: NHL Sensor]
    scan_interval: [(Optional) SCAN INTERVAL IN SECONDS - DEFAULT: 5]
```
## Documentation:
Please refer to the [documentation](https://github.com/JayBlackedOut/hass-nhlapi/) in the repository.
