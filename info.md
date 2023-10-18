# <span style="color:red">Breaking Change!</span>
On September 21, 2023, the NHL started retiring their API endpoints and introduced a new API. Like the previous API, the new one is public but undocumented/not publicized. This custom component has been reworked to consume the new API. Every effort has been made to provide a like-for-like experience for existing users.

**Breaking Changes introduced in this update:**
* `team_id` has been replaced with `team_abbrev` as a YAML configuration key.
* Users will now need to use the 3 letter abbreviation of the team they wish to track instead of the numeric team ID.
* the `last_goal` attribute has been removed from the exposed information since the new API does not readily provide human readable goal descriptions.

Help the effort to continue documenting the new endpoints by joining the fine folks in the [NHL LED Scoreboard discord](https://discord.gg/CWa5CzK)!

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
