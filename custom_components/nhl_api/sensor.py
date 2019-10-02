"""
Support for the undocumented NHL API.

For more details about this platform, please refer to the documentation at
https://github.com/JayBlackedOut/hass-nhlapi/blob/master/README.md
"""
# TODO: Add suppport for events
# TODO: Convert attribute 'next_game_time' from UTC to local
import logging
from datetime import timedelta
from pynhl import Schedule, Scoring
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_ID, CONF_SCAN_INTERVAL)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

__version__ = '0.3.1'

CONF_ID = 'team_id'
CONF_NAME = 'name'

DEFAULT_NAME = 'NHL Sensor'

LOGO_URL = 'https://www-league.nhlstatic.com/images/logos/'\
    'teams-current-primary-light/{}.svg'

SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID, default=0): cv.positive_int,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the NHL API sensor."""
    team_id = config.get(CONF_ID)
    name = config.get(CONF_NAME, DEFAULT_NAME)
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    add_entities([NHLSensor(team_id, name, scan_interval)], True)


class NHLSensor(Entity):
    """Representation of a NHL API sensor."""

    def __init__(self, team_id, name, scan_interval):
        """Initialize NHL API sensor."""
        self._state = None
        self.team_id = team_id
        self._name = name
        self._icon = 'mdi:hockey-sticks'
        self._scan_interval = scan_interval
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
        """Get the latest data from the NHL API via pynhl."""
        games = Schedule(self.team_id).game_info()
        dates = Schedule(self.team_id).datetime_info()
        if Scoring(self.team_id).scoring_info() is not None:
            plays = Scoring(self.team_id).scoring_info()
        else:
            plays = {}
        all_attr = {**games, **plays, **dates}
        # Set sensor state to game state.
        # Display next game date if none today.
        self._state = plays.get('game_state', all_attr.get('next_game_date'))
        # Set sensor state attributes
        self._state_attributes = all_attr
        # Set away team logo url as attribute 'away_logo'.
        self._state_attributes['away_logo'] = \
            LOGO_URL.format(self._state_attributes.get('away_id'))
        # Set home team logo url as attribute 'home_logo'.
        self._state_attributes['home_logo'] = \
            LOGO_URL.format(self._state_attributes.get('home_id'))
        # Set attribute for goal scored by tracked team.
        if self._state_attributes.get('goal_team_id', None) == self.team_id:
            self._state_attributes['goal_tracked_team'] = True
        else:
            self._state_attributes['goal_tracked_team'] = False
