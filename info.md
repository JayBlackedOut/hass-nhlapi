## Information
Track the score of your favorite NHL team and create automations based on your team scoring!

See [example automations](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md) to help you get started.



## Setup
After installing in HACS, set up via Settings > Devices & Services > Add Integration then search for "NHL API". You will need to specify the 3 letter abbreviation of the team you'd like to track. You may also optionally set up a longer scan interval in seconds for live games.

**<font color="red">Warning:</font> Setting up the integration via configuration.yaml will be deprecated in version 2.0.0.**

Add to configuration.yaml:

```
sensor:
  - platform: nhl_api
    team_abbrev: [TEAM ABBREV OF TRACKED TEAM - REFER TO DOCS]
    name: [(Optional) FRIENDLY NAME OF SENSOR - DEFAULT: NHL Sensor]
    scan_interval: [(Optional) SCAN INTERVAL IN SECONDS FOR LIVE GAME - DEFAULT: 1]
```
## Documentation
Please refer to the [documentation](https://github.com/JayBlackedOut/hass-nhlapi/) in the repository.
