[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
# Home Assistant NHL API
NHL Stats API Integration Into Home Assistant
## Installation: Manual
1. Copy the `nhl_api` folder to the `custom_components` folder in your Home Assistant configuration directory.
2. From the [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md) file in this repository, find the team_id of the team you would like to track.
3. Restart Home Assistant to allow the required packages to be installed.
4. Add the following minimum code in your `configuration.yaml` file. See Configuration for more advanced options:
```
sensor:
  - platform: nhl_api
    team_id: [TEAM ID FOUND IN STEP 2].
```
5. Restart Home Assistant one final time.
## Installation: HACS
This method assumes you have HACS already installed.
1. In the HACS Store, search for `NHL` and find the `NHL API` integration and install it.
2. From the [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md) file in this repository, find the team_id of the team you would like to track.
3. Restart Home Assistant to allow the required packages to be installed.
4. Add the following code in your `configuration.yaml` file. See Configuration for more advanced options:
```
sensor:
  - platform: nhl_api
    team_id: [TEAM ID FOUND IN STEP 2].
```
5. Restart Home Assistant one final time.
## Configuration
| key      | required | type    | usage                                                                                                                               |
|----------|----------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| platform | true     | string  | `nhl_api`                                                                                                                           |
| team_id  | true     | integer | Identifies the team to be tracked by the sensor. See [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md). |
| name     | false    | string  | Friendly name of the sensor. If not defined, defaults to: 'NHL Sensor'.                                                             |
| scan_interval | false    | integer  | Number of seconds until the sensor updates its state. If not defined, defaults to 5 seconds.                                                             |

Warning! Setting your `scan_interval` to a low number leads to more writes to your disk. It is recommended to not set the scan interval to less than 5 if running Home Assistant on a Raspberry Pi. Also, each time the sensor updates (i.e. at each scan interval), anywhere from ~300B to ~25KB of data is consumed. Keep this in mind if you have a low internet data cap.

## Exposed Information
The sensor will expose the status of the tracked team's scheduled game for the day. The state can be:

| state                  | description                                                                               |
|------------------------|-------------------------------------------------------------------------------------------|
| Next Game Date & Time  | The next game is not yet close to starting. Will return date and time of the next game.  |
| Pre-Game               | The scheduled game is with 30 minutes of its scheduled start.                             |
| In Progess             | The scheduled game is live.                                                               |
| In Progress - Critical | The scheduled game is within 5 minutes of the 3rd period's end.                           |
| Game Over              | The scheduled game has recently ended.                                                    |
| Final                  | The scheduled game is over and the score is final.                                        |

The sensor will return the following state attributes whether or not a game is in progress:

| attribute         | type    | usage                                                                                                                                                                                     |
|-------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| away_id           | integer | Identifies the away team by team id as found in [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md).                                                         |
| home_id           | integer | Identifies the home team by team id as found in [teams.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/teams.md).                                                         |
| away_name         | string  | The name of the away team.                                                                                                                                                                |
| home_name         | string  | The name of the home team.                                                                                                                                                                |
| away_logo         | string  | The url to the away team's logo.                                                                                                                                                          |
| home_logo         | string  | The url to the home team's logo.                                                                                                                                                          |
| next_game_date    | string  | The date of the next game.                                                                                                                                                                |
| next_game_time    | string  | The time of the next game. This will be localized based on your Home Assistant configured timezone.                                                                                  |

The sensor will also return the following state attributes when a game is in progress:

| attribute         | type    | usage                                                             |
|-------------------|---------|-------------------------------------------------------------------|
| last_goal         | string  | Description of the last goal scored in the format "GoalScorer (Season/PlayoffTotal) TypeOfShot, assists: AssistingPlayer1 (Season/PlayoffTotal), AssistingPlayer2 (Season/PlayoffTotal)".        |
| goal_type         | string  | At what strength the goal was scored such as EVEN, PPG, SHG, etc. |
| goal_team_id      | integer | The id of the team that scored the last goal.                     |
| goal_event_id     | integer | The event id of the goal generated by the API.                    |
| goal_team_name    | string  | The name of the team that scored the last goal.                   |
| away_score        | integer | The number of goals scored by the away team.                      |
| home_score        | integer | The number of goals scored by the home team.                      |
| goal_tracked_team | boolean | Returns `true` if the last goal was scored by the team being tracked. Otherwise, returns `false`. Can be useful for goal alerts.                                                                    |

## Examples
Display info in the front end: [frontend.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/frontend.md)  
Sample automations: [automations.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/automations.md)

## Objectives Checklist
- [x] Consume undocumented NHL Stats API locally with the least amount of resources possible.
- [x] Pass information to Home Assistant as sensor data. (ex. Next game scheduled, live scores, goal description, etc.)
- [x] Create a "goal" event platform to use as a trigger for automations.
- [ ] Display the information in the front-end in its own Lovelace card.
- [x] Add support for `HACS`.
## Resources
[The Undocumented NHL Stats API](https://statsapi.web.nhl.com/api/v1/schedule)

[Drew Hynes' Unofficial Documentation](https://gitlab.com/dword4/nhlapi)

[Adam Pritchard's NHL Score API](https://github.com/peruukki/nhl-score-api)

[The Reddit Post that Inspired this Project](https://www.reddit.com/r/homeassistant/comments/b9vioe/got_home_assistant_to_grab_the_game_info_for_my/)
