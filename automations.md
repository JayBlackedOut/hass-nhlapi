# Automation Examples (Version 0.5.0 and After)
As of Version 0.5.0, every time a goal is scored during a tracked game (i.e. a game being played by a tracked team), the `nhl_goal` event will fire with the scoring team's ID as event data. This makes it incredibly easy to use goals to trigger automations. No extra template_sensors or input_numbers have to be set-up. Only the minimum configuration has to exist in `configuration.yaml`.

## Configuration

`automations.yaml`

The automation below will announce a Montreal Canadiens goal on the living room speaker with text-to-speech. Remember to wrap the team_id value in double-quotes or the automation will not fire.

```
- alias: 'Montreal Goal Announcement'
  trigger:
    platform: event
    event_type: nhl_goal
    event_data:
      team_id: "8"
  action:
    service: tts.google_translate_say
    entity_id: media_player.living_room_speaker
    data:
      message: 'The habs scored!'
```

# Automation Examples (All Versions)
All credit goes to @Jazz#7670 on Discord for the automations below. All these automations assume you have set up the template sensors as shown in [frontend.md](https://github.com/JayBlackedOut/hass-nhlapi/blob/master/frontend.md) and are using the default name for the sensor, `sensor.nhl_sensor`. Adjust as necessary.

## Configuration

`configuration.yaml`

Add 2 `input_number` components to keep track of the score prior to a goal.

```
input_number:
  away_score:
    min: 0
    max: 100
  home_score:
    min: 0
    max: 100
```

`automations.yaml`

Set the score tracking input numbers to 0 prior to the start of the game:

```
- id: reset_score
  alias: reset_score
  initial_state: true
  trigger:
    platform: state
    entity_id: sensor.nhl_hockey
    from: "Scheduled"
    to: "Pre-Game"
  action:
  - service: input_number.set_value
    entity_id: input_number.home_score
    data:
      value: 0
  - service: input_number.set_value
    entity_id: input_number.away_score
    data:
      value: 0
```

Announce that the away team has scored over text-to-speech. For example, if the Pittsburgh Penguins are the away team and they score, the tts would say "Pittsburgh Penguins score!":

```
- id: away_scores
  alias: away_scores
  initial_state: true
  trigger:
  - platform: template
    value_template: "{{ states.sensor.away_team.state  | int > states('numeric_input.away_score') | int }}"
  action:
  - service: input_number.set_value
    entity_id: numeric_input.away_score
    data_template: 
      value: "{{ states.sensor.away_team.state |int }}"
  - service: notify.alexa_media
    data:
      target: 
        - "Living room Dot"
      message: "{{ state_attr( 'sensor.away_team', 'friendly_name') }} score!"
      data: 
        type: "tts" 
```
Announce that the home team has scored over text-to-speech. For example, if the Montreal Canadiens are the home team and they score, the tts would say "Montreal Canadiens score!":

```
- id: home_scores
  alias: home_scores
  initial_state: true
  trigger:
  - platform: template
    value_template: "{{ states.sensor.home_team.state  | int > states('numeric_input.home_score') | int }}"
  action:
  - service: input_number.set_value
    entity_id: numeric_input.home_score
    data_template: 
      value: "{{ states.sensor.home_team.state |int }}"
  - service: notify.alexa_media
    data:
      target: 
        - "Living room Dot"
      message: "{{ state_attr( 'sensor.home_team', 'friendly_name') }} score!"
      data: 
        type: "tts"
```

Play a goal horn mp3 over a speaker when the tracked team scores. Here, we use a delay of 25 seconds. This should be adjusted so that the horn sounds at the same time as the goal is scored on your TV to account for broadcast/stream delays:

```
- id: predators_score
  alias: predators_score
  initial_state: true
  trigger:
    platform: template
    value_template: "{{ states.sensor.away_team.state |int > states.numeric_input.away_score |int or 
states.sensor.home_team.state |int > states.numeric_input.home_score |int }}"
  condition:
    condition: template
    value_template: "{{ state_attr('sensor.nhl_sensor', 'goal_tracked_team') }}"
  action:
  - service: script.home_wave
    data:
      delay: 00:00:25
      wave: "goal-horns.mp3"
      home_entity: media_player.living_room_speaker
```

Announce the final score over text-to-speech:

```
- id: final_score
  alias: final_score
  initial_state: true
  trigger:
    platform: state
    entity_id: sensor.nhl_hockey
    from: "Game Over"
    to: "Final"
  action:
  - service: notify.alexa_media
    data:
      target: 
        - "Living room Dot"
      message: "Final Score: {{ state_attr( 'sensor.away_team', 'friendly_name') }} {{ states('sensor.away_team') }},, {{ state_attr( 'sensor.home_team', 'friendly_name') }}{{ states('sensor.home_team') }} !"
      data: 
        type: "tts"
```