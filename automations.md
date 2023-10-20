# Automation Examples
Every time a goal is scored during a tracked game (i.e. a game being played by a tracked team), the `nhl_goal` event will fire with the scoring team's ID as event data. This makes it incredibly easy to use goals to trigger automations. No extra template_sensors or input_numbers have to be set-up. Only the minimum configuration has to exist in `configuration.yaml`.

## Configuration

`automations.yaml`

The automation below will announce a Montreal Canadiens goal on the living room speaker with text-to-speech. Remember to wrap the team_id value in double-quotes or the automation will not fire.

With the addition of `goal_tracked_team` to the event data in version 0.9.0, you no longer have to use your tracked team's ID in the trigger.

```
- alias: 'Montreal Goal Announcement'
  trigger:
    platform: event
    event_type: nhl_goal
    event_data:
      goal_tracked_team: true
  action:
    service: tts.google_translate_say
    entity_id: media_player.living_room_speaker
    data:
      message: 'The habs scored!'
```

Alternatively, you can still match against the `team_abbrev`. MUST BE UPPERCASE:

```
- alias: 'Montreal Goal Announcement'
  trigger:
    platform: event
    event_type: nhl_goal
    event_data:
      team_abbrev: MTL
  action:
    service: tts.google_translate_say
    entity_id: media_player.living_room_speaker
    data:
      message: 'The habs scored!'
```