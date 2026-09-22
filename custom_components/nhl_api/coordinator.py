"""Shared NHL polling and goal notifications."""

from __future__ import annotations

from datetime import datetime as dt, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util
from pynhl import NHLApiError, NHLApiTimeoutError, Plays, Schedule

from .const import DEFAULT_NAME, DOMAIN
from .goals import GoalTracker

_LOGGER = logging.getLogger(__name__)


class NHLCoordinator(DataUpdateCoordinator[tuple[dict, str]]):
    """Fetch once per team and publish new goals on the event loop."""

    def __init__(
        self, hass: HomeAssistant, team_abbrev: str, scan_interval: timedelta,
        entry: ConfigEntry | None = None,
    ) -> None:
        super().__init__(
            hass, _LOGGER, name=f"NHL {team_abbrev.upper()}",
            config_entry=entry, update_interval=scan_interval,
        )
        self.team_abbrev = team_abbrev
        self.scan_interval = max(scan_interval, timedelta(seconds=1))
        self.goals = GoalTracker()
        self.goal_sequence = 0
        self.last_goal: dict | None = None
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, team_abbrev)},
            name=f"{DEFAULT_NAME} {team_abbrev.upper()}", manufacturer="NHL",
        )

    async def _async_update_data(self) -> tuple[dict, str]:
        attributes, next_date_time = await self.hass.async_add_executor_job(
            self.get_game_data
        )
        attributes["goal_tracked_team"] = (
            attributes.get("goal_team_abbrev") == self.team_abbrev.upper()
        )
        game_state = attributes.get("game_state")
        if game_state == "PRE":
            self.update_interval = timedelta(seconds=10)
        elif game_state in (None, "LIVE", "CRIT", "FINAL"):
            self.update_interval = self.scan_interval
        else:
            self.update_interval = timedelta(seconds=600)

        if self.goals.is_new_goal(attributes):
            self.goal_sequence += 1
            self.last_goal = {
                "team_abbrev": attributes["goal_team_abbrev"],
                "goal_tracked_team": attributes["goal_tracked_team"],
                "game_id": attributes["game_id"],
                "goal_event_id": attributes["goal_event_id"],
                "tracked_team_abbrev": self.team_abbrev.upper(),
            }
            # Keep the existing event name and payload for existing automations.
            self.hass.bus.async_fire("nhl_goal", {
                "team_abbrev": self.last_goal["team_abbrev"],
                "goal_tracked_team": self.last_goal["goal_tracked_team"],
            })
        if game_state in ("FUT", "No Game Scheduled"):
            state = next_date_time.strip()
        else:
            state = attributes.get("game_state", next_date_time.strip())
        return attributes, state

    def get_game_data(self) -> tuple[dict, str]:
        """Get the latest data from the NHL API via pynhl."""
        try:
            schedule = Schedule(self.team_abbrev)

            games = schedule.game_info() or {}
            dates = schedule.datetime_info() or {}
            broadcasts = schedule.broadcast_info() or {}

        except NHLApiTimeoutError:
            raise UpdateFailed("Request timed out fetching schedule data") from None

        except NHLApiError as err:
            raise UpdateFailed(f"Error fetching schedule data: {err}") from err

        game_id = games.get("game_id")

        plays = {}
        linescore = {}

        if game_id:
            try:
                plays_obj = Plays(game_id)
                plays = plays_obj.scoring_info() or {}
                linescore = plays_obj.linescore_info() or {}

            except NHLApiTimeoutError:
                raise UpdateFailed("Request timed out fetching play data") from None

            except NHLApiError as err:
                raise UpdateFailed(f"Error fetching play data: {err}") from err

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
                "next_game_time": dttm_local.strftime("%I:%M %p").lstrip("0"),
                "next_game_datetime": dttm_local,
            }

            next_game_date = f"{dttm_local:%B} {dttm_local.day}, {dttm_local:%Y}"

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

