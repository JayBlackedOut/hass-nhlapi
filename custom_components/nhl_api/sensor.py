"""
Support for the undocumented NHL API.

For more details about this platform, please refer to the documentation at
https://github.com/JayBlackedOut/hass-nhlapi/blob/master/README.md
"""
import logging
from datetime import timedelta

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_ID)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

__version__ = '0.1.0'

CONF_ID = 'team_id'
CONF_NAME = 'name'

DEFAULT_NAME = 'NHL Sensor'

API_URL = 'https://statsapi.web.nhl.com/api/v1/schedule?'\
    'hydrate=scoringplays&teamId={}'

LOGO_URL = 'https://www-league.nhlstatic.com/images/logos/'\
    'teams-current-circle/{}.svg'

SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID, default=0): cv.positive_int,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the NHL API sensor."""
    team_id = config.get(CONF_ID)
    if config.get(CONF_NAME) is None:
        name = DEFAULT_NAME
    else:
        name = config.get(CONF_NAME)
    add_entities([NHLSensor(team_id, name)], True)


class NHLSensor(Entity):
    """Representation of a NHL API sensor."""

    def __init__(self, team_id, name):
        """Initialize NHL API sensor."""
        self._state = API_URL
        self._team_id = team_id
        self._name = name
        self._icon = 'mdi:hockey-sticks'
        self._state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    def update(self):
        """Get the latest data from the NHL API."""
        url = API_URL.format(self._team_id)
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            data = response.json()
            totalItems = data['totalItems']
            """Check if a game is scheduled."""
            if totalItems == 1:
                """Retrieve latest game state."""
                games = data['dates'][0]['games']
                self._state = games[0]['status']['detailedState']
                self._state_attributes['away_id'] = \
                    games[0]['teams']['away']['team']['id']
                self._state_attributes['home_id'] = \
                    games[0]['teams']['home']['team']['id']
                self._state_attributes['away_logo'] = \
                    LOGO_URL.format(self._state_attributes['away_id'])
                self._state_attributes['home_logo'] = \
                    LOGO_URL.format(self._state_attributes['home_id'])
                self._state_attributes['away_name'] = \
                    games[0]['teams']['away']['team']['name']
                self._state_attributes['home_name'] = \
                    games[0]['teams']['home']['team']['name']
                self._state_attributes['away_score'] = \
                    games[0]['teams']['away']['score']
                self._state_attributes['home_score'] = \
                    games[0]['teams']['home']['score']
                scoringPlays = \
                    games[0]['scoringPlays']
                if len(scoringPlays) > 0:
                    self._state_attributes['description'] = \
                        scoringPlays[-1]['result']['description']
                    if scoringPlays[-1]['team']['id'] == self._team_id:
                        self._state_attributes['goal_tracked_team'] = True
                    else:
                        self._state_attributes['goal_tracked_team'] = False
                else:
                    self._state_attributes['description'] = "No goals scored"
                    self._state_attributes['goal_tracked_team'] = False
            else:
                self._state = "No Game Scheduled"
