# Goal automations

UI-configured teams now expose a Goal event entity alongside the existing sensor,
for example `event.nhl_mtl_goal`. Check your entity registry for the actual ID.
The event entity follows Home Assistant's [event entity design](https://developers.home-assistant.io/docs/core/entity/event/).
Its state is the timestamp when a new goal was observed. Attributes include
`event_type: goal`, `team_abbrev` (scoring team), `goal_tracked_team`,
`tracked_team_abbrev`, `game_id`, and `goal_event_id`.

Use a state trigger on the timestamp, not on the `event_type` attribute: consecutive
goals have the same event type. This example announces goals for the tracked team:

```yaml
- alias: Montreal goal announcement
  triggers:
    - trigger: state
      entity_id: event.nhl_mtl_goal
      not_from:
        - unavailable
      not_to:
        - unknown
        - unavailable
  conditions:
    - condition: template
      value_template: >-
        {{ trigger.from_state is not none
           and trigger.to_state is not none
           and trigger.to_state.attributes.get('event_type') == 'goal'
           and trigger.to_state.attributes.get('goal_tracked_team', false) }}
  actions:
    - action: tts.speak
      target:
        entity_id: tts.your_tts_provider
      data:
        media_player_entity_id: media_player.living_room_speaker
        message: The Habs scored!
```

Replace the entity IDs with your own. The conditions and unavailable guard prevent
initial entity creation and availability recovery from announcing old goals.
The first goal from an unknown state is allowed. A goal first observed when the
entity recovers from being unavailable is skipped by this example; for delivery
on that transition, use the compatible `nhl_goal` bus trigger below.

The first successful poll after setup establishes a baseline without announcing
an existing goal. Repeated polls, including `FINAL`, do not replay the same goal.
Goal IDs are scoped to their game. Polling reads the latest goal supplied by
`pynhl`; it cannot recover every goal if several occur between successful polls.

Existing `nhl_goal` automations remain supported, including legacy YAML sensor
setups. Migrate a YAML-configured team to the integration UI to get the new event
entity. Use one trigger approach per automation to avoid announcing a goal twice.

## Existing event-bus automations

Each newly detected goal fires `nhl_goal` with `team_abbrev` and
`goal_tracked_team`. This works with both UI and legacy YAML setup.

## Configuration

`automations.yaml`

The automation below will announce a Montreal Canadiens goal on the living room speaker with text-to-speech.

With the addition of `goal_tracked_team` to the event data in version 0.9.0, you no longer have to use your tracked team's ID in the trigger.

```
- alias: 'Montreal Goal Announcement'
  trigger:
    platform: event
    event_type: nhl_goal
    event_data:
      goal_tracked_team: true
  action:
    action: tts.speak
    target:
      entity_id: tts.your_tts_provider
    data:
      media_player_entity_id: media_player.living_room_speaker
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
    action: tts.speak
    target:
      entity_id: tts.your_tts_provider
    data:
      media_player_entity_id: media_player.living_room_speaker
      message: 'The habs scored!'
```