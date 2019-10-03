"""The NHL API integration."""

DOMAIN = 'nhl_api'


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    # Fire event example_component_my_cool_event with event data answer=42
    hass.bus.fire('nhl_api_goal', {
        'goal_team_id': goal_team_id
    })

    # Return successful setup
    return True
