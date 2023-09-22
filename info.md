# <span style="color:red">Breaking Change!</span>
On September 21, 2023, the NHL retired their API endpoints and introduced a new API. Like the previous API, the new one is public but undocumented/not publicized. Efforts are underway to map the new endpoints. Once completed, this custom component will be reworked to consume the new API. Until then, it will sadly no longer function.

Help the effort to document the new endpoint by joining the fine folks in the [NHL LED Scoreboard discord](https://discord.gg/CWa5CzK)!

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
