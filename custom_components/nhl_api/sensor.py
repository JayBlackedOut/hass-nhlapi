"""
Support for the undocumented NHL API.
For more details about this platform, please refer to the documentation at
https://github.com/JayBlackedOut/hass-nhlapi/blob/master/README.md
"""

from __future__ import annotations

from datetime import datetime as dt
from datetime import timedelta
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
    AddEntitiesCallback,
)
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.util.dt as dt_util
from pynhl import NHLApiError, NHLApiTimeoutError, Plays, Schedule
import voluptuous as vol

from .const import (
    CONF_ABBREV,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PREGAME_SCAN_INTERVAL = timedelta(seconds=10)
LIVE_SCAN_INTERVAL = timedelta(seconds=1)
POSTGAME_SCAN_INTERVAL = timedelta(seconds=600)


# Legacy YAML configuration support.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ABBREV): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
        ): cv.time_period,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the NHL API sensor from configuration.yaml (legacy)."""
    _LOGGER.warning(
        "Configuration of NHL API via configuration.yaml is deprecated and will be "
        "removed in version 2.0.0. Please migrate to the UI-based setup under "
        "Settings -> Devices & Services -> Add Integration -> NHL API."
    )

    team_abbrev = config[CONF_ABBREV].strip().lower()
    scan_interval = config.get(
        CONF_SCAN_INTERVAL,
        DEFAULT_SCAN_INTERVAL,
    )

    async_add_entities(
        [
            NHLSensor(
                team_abbrev,
                timedelta(seconds=scan_interval),
            )
        ]
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the NHL sensor from a config entry."""
    team_abbrev = entry.data[CONF_ABBREV].strip().lower()

    scan_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
    )

    async_add_entities(
        [
            NHLSensor(
                team_abbrev,
                scan_interval,
            )
        ]
    )


class NHLSensor(SensorEntity):
    """Representation of an NHL API sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:hockey-sticks"
    _attr_name = None

    def __init__(
        self,
        team_abbrev: str,
        scan_interval: timedelta,
    ) -> None:
        """Initialize NHL API sensor."""
        self._state: str | None = None
        self._team_abbrev = team_abbrev.lower()
        self._scan_interval = scan_interval
        self._last_scan = dt.today()
        self._state_attributes: dict = {}
        self._fired_events: list[str] = []

        self._attr_unique_id = f"{DEFAULT_NAME.lower()}_{self._team_abbrev}"

        team_name = f"{DEFAULT_NAME} {self._team_abbrev.upper()}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._team_abbrev)},
            name=team_name,
            manufacturer="NHL",
        )

    async def async_added_to_hass(self) -> None:
        """Start the update timer once the entity is registered with Home Assistant."""
        self.timer(dt.today())

    @callback
    def timer(self, nowtime: dt) -> None:
        """Schedule the next update based on the dynamic polling interval."""
        self.async_schedule_update_ha_state(True)

        polling_delta = self.set_polling()
        nexttime = nowtime + polling_delta

        async_track_point_in_time(
            self.hass,
            self.timer,
            nexttime,
        )

    @property
    def native_value(self) -> str | None:
        """Return the value of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes of the sensor."""
        return self._state_attributes

    def get_game_data(self) -> tuple[dict, str]:
        """Get the latest data from the NHL API via pynhl."""
        try:
            schedule = Schedule(self._team_abbrev)

            games = schedule.game_info() or {}
            dates = schedule.datetime_info() or {}
            broadcasts = schedule.broadcast_info() or {}

        except NHLApiTimeoutError:
            _LOGGER.warning("Request timed out fetching schedule data")
            return {}, ""

        except NHLApiError as err:
            _LOGGER.error("Error fetching schedule data: %s", err)
            return {}, ""

        game_id = games.get("game_id")

        plays = {}
        linescore = {}

        if game_id:
            try:
                plays_obj = Plays(game_id)
                plays = plays_obj.scoring_info() or {}
                linescore = plays_obj.linescore_info() or {}

            except NHLApiTimeoutError:
                _LOGGER.warning("Request timed out fetching play data")
                return {}, ""

            except NHLApiError as err:
                _LOGGER.error("Error fetching play data: %s", err)
                return {}, ""

        if (
            dates.get("next_game_datetime")
            and dates["next_game_datetime"] != "None"
        ):
            dttm = dt.strptime(
                dates["next_game_datetime"],
                "%Y-%m-%dT%H:%M:%S%z",
            )

            dttm_local = dt_util.as_local(dttm)

            time = {
                "next_game_time": dttm_local.strftime("%-I:%M %p"),
                "next_game_datetime": dttm_local,
            }

            next_game_date = dttm_local.strftime("%B %-d, %Y")

            now = dt_util.as_local(dt.now())

            pick = {
                now.strftime("%Y-%m-%d"): "Today,",
                (now + timedelta(days=1)).strftime("%Y-%m-%d"): "Tomorrow,",
            }

            game_date = pick.get(
                dttm_local.strftime("%Y-%m-%d"),
                next_game_date,
            )

        else:
            time = {
                "next_game_time": "",
                "next_game_datetime": "",
            }

            game_date = "No Game Scheduled"
            next_game_date = ""

        next_game = {
            "next_game_date": next_game_date,
        }

        all_attr = {
            **broadcasts,
            **linescore,
            **games,
            **plays,
            **time,
            **next_game,
        }

        next_date_time = game_date + " " + time["next_game_time"]

        return all_attr, next_date_time

    def _update_fired_events(
        self,
        event_id: str = "0",
        clear: bool = False,
    ) -> list[str]:
        """Track which goal event IDs have already been fired."""
        if clear:
            self._fired_events = []
            return self._fired_events

        self._fired_events.append(event_id)
        self._fired_events = list(set(self._fired_events))

        return self._fired_events

    def _handle_goal_event(
        self,
        goal_team_abbrev: str | None,
        goal_event_id: str | None,
        goal_tracked_team: bool | None,
    ) -> None:
        """Fire a goal event if it hasn't already been fired for this goal."""
        if goal_event_id is None:
            return

        event_id = str(goal_event_id)

        if event_id not in self._fired_events:
            self.hass.bus.fire(
                "nhl_goal",
                {
                    "team_abbrev": goal_team_abbrev,
                    "goal_tracked_team": goal_tracked_team,
                },
            )

        self._update_fired_events(event_id)

    def set_state(self) -> str | None:
        """Set sensor state to game state and set polling interval."""
        all_attr, next_date_time = self.get_game_data()

        if all_attr.get("game_state") in ["FUT", "No Game Scheduled"]:
            self._state = next_date_time.strip()
        else:
            self._state = all_attr.get(
                "game_state",
                next_date_time.strip(),
            )

        self._state_attributes = all_attr

        if (
            self._state_attributes.get("goal_team_abbrev")
            == self._team_abbrev.upper()
        ):
            self._state_attributes["goal_tracked_team"] = True
        else:
            self._state_attributes["goal_tracked_team"] = False

        self._handle_goal_event(
            self._state_attributes.get("goal_team_abbrev"),
            self._state_attributes.get("goal_event_id"),
            self._state_attributes.get("goal_tracked_team"),
        )

        if self._state == "FINAL":
            self._update_fired_events(clear=True)

        return self._state

    def set_polling(self) -> timedelta:
        """Set dynamic polling interval."""
        game_state = self._state

        if game_state == "PRE":
            polling_delta = PREGAME_SCAN_INTERVAL

        elif game_state in [None, "LIVE", "CRIT", "FINAL"]:
            if self._scan_interval > LIVE_SCAN_INTERVAL:
                polling_delta = self._scan_interval
            else:
                polling_delta = LIVE_SCAN_INTERVAL

        else:
            polling_delta = POSTGAME_SCAN_INTERVAL

        return polling_delta

    def update(self) -> None:
        """Update the sensor."""
        self.set_state()
