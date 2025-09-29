## Information:
Track the score of your favorite NHL team and create automations based on your team scoring!

See [example automations](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md) to help you get started.



## Usage:
Add to configuration.yaml:

```
sensor:
  - platform: nhl_api
    team_abbrev: [TEAM ABBREV OF TRACKED TEAM - REFER TO DOCS]
    name: [(Optional) FRIENDLY NAME OF SENSOR - DEFAULT: NHL Sensor]
    scan_interval: [(Optional) SCAN INTERVAL IN SECONDS FOR LIVE GAME - DEFAULT: 1]
```
## Documentation:
Please refer to the [documentation](https://github.com/JayBlackedOut/hass-nhlapi/) in the repository.
