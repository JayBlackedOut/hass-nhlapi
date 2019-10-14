**New in Version 0.5.0!** Trigger your automations with the `nhl_goal` event platform. See the [example automations](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md) for more information.

## Information:
Track the score of your favorite NHL team and create automations based on your team scoring!

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
