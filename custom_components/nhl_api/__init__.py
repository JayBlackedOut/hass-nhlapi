"""The NHL API integration."""

from .sensor import NHLSensor

DOMAIN = 'nhl_api'


def setup(hass, config):
    """Home Assistant is loading our component."""
    fired_event_id = []


def goal_event_handler(hass):
    """Handle firing of the goal event."""
    goal_team_id = NHLSensor._state_attributes.get('goal_team_id', None)
    goal_event_id = NHLSensor._state_attributes.get('goal_event_id', None)
    # If the event hasn't yet been fired for this goal, fire it.
    if setup.fired_event_id != [] and \
            goal_event_id not in setup.fired_event_id:
        hass.bus.fire('nhl_api_goal', {'team_id': goal_team_id})
        setup.fired_event_id.append(goal_event_id)
    # At game end, reset the list of fired events.
    if NHLSensor._state == "Final":
        setup.fired_event_id = []
