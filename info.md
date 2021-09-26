<span style="color:red">*Important!*</span> There was a breaking change introduced in Home Assistant 2021.8.X that renders the state of the `away_team` and `home_team` template sensors unknown. Please see the [new instructions](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/frontend.md) for formatting these sensors for use in the front end.

## Information:
Track the score of your favorite NHL team and create automations based on your team scoring!

**New as of Version 0.9.0!** The `nhl_goal` event platform will now also pass if the goal was scored by the tracked team or the other team. See the [example automations](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md) for more information.



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
