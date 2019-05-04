# Home Assistant NHL API
NHL Stats API Integration Into Home Assistant
## Installation
1. Copy the `nhl_api` folder to the `custom_components` folder in your Home Assistant configuration directory.
2. From the [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md) file in this repository, find the team_id of the team you would like to track.
3. Add the following code in your `configuration.yaml` file:
```
sensor:
  - platform: nhl_api
    team_id: $id # <-- replace $id with the Team ID found in step 2.
```
## Configuration
| key      | required | type    | usage                                                                                                                               |
|----------|----------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| platform | true     | string  | `nhl_api`                                                                                                                           |
| team_id  | true     | integer | Identifies the team to be tracked by the sensor. See [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md). |
| name     | false    | string  | Friendly name of the sensor. If not defined, defaults to: 'NHL Sensor'.                                                             |
## Objectives
* Consume undocumented NHL Stats API locally with the least amount of resources possible.
* Pass information to Home Assistant as sensor data. (ex. Next game scheduled, live scores or recent scores, goal description, etc.)
* Create a "goal" event platform to use as a trigger for automations.
* Display the information in the front-end in its own Lovelace card.
## Resources
[The Undocumented NHL Stats API](https://statsapi.web.nhl.com/api/v1/schedule)

[Drew Hynes' Unofficial Documentation](https://gitlab.com/dword4/nhlapi)

[Adam Pritchard's NHL Score API](https://github.com/peruukki/nhl-score-api)

[The Reddit Post that Inspired this Project](https://www.reddit.com/r/homeassistant/comments/b9vioe/got_home_assistant_to_grab_the_game_info_for_my/)
