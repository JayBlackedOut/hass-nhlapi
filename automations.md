# Goal automations

## Using the automation editor

On Home Assistant 2026.7 or newer, use the built-in
[Event received trigger](https://www.home-assistant.io/triggers/event.received/):

1. Create an automation and add a trigger.
2. Select your team's **Goal** entity, then **Event received**.
3. Select the event type **goal**.
4. Add a **State** condition for the same entity: attribute
   **goal_tracked_team**, value **true**. This excludes opponent goals.
5. Choose your action, such as announcing the goal or flashing a light.

The Goal entity is available for teams configured through the integration UI.
Its ID is typically `event.nhl_[team_abbrev]_goal`; check your installation for the actual ID.

## YAML example

Replace the entity IDs with your own:

```yaml
- alias: Montreal goal announcement
  triggers:
    - trigger: event.received
      target:
        entity_id: event.nhl_mtl_goal
      options:
        event_type:
          - goal
  conditions:
    - condition: state
      entity_id: event.nhl_mtl_goal
      attribute: goal_tracked_team
      state: true
  actions:
    - action: tts.speak
      target:
        entity_id: tts.your_tts_provider
      data:
        media_player_entity_id: media_player.living_room_speaker
        message: The Habs scored!
```

## Older versions and existing automations

The integration still supports Home Assistant 2026.3+. If **Event received** is
not available, or your team uses legacy YAML setup, use the compatible `nhl_goal`
bus trigger. Existing automations keep working. For example, replace the trigger
and condition above with:

```yaml
  triggers:
    - trigger: event
      event_type: nhl_goal
      event_data:
        team_abbrev: MTL
  conditions: []
```

Use uppercase team abbreviations. Use one trigger approach per automation to
avoid announcing a goal twice.

## Goal detection

The first successful poll after setup establishes a baseline without announcing
an existing goal. Repeated polls, including `FINAL`, do not replay the same goal.
The API supplies the latest goal, so multiple goals between successful polls may
not all be detected.
