"""Exercise NHL delivery with small doubles for the unavailable HA runtime.

These tests check our executor boundary and event handling, not HA's scheduler.
"""

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock
from datetime import timedelta

import pytest

ROOT = Path(__file__).parents[1] / "custom_components/nhl_api"


@pytest.fixture
def integration(monkeypatch):
    def module(name, **values):
        result = ModuleType(name)
        result.__dict__.update(values)
        monkeypatch.setitem(sys.modules, name, result)
        return result

    class Coordinator:
        def __class_getitem__(cls, item):
            return cls

        def __init__(self, hass, logger, **kwargs):
            self.hass = hass
            self.last_update_success = True

    class Entity:
        def __class_getitem__(cls, item):
            return cls

        def __init__(self, coordinator):
            self.coordinator = coordinator
            self.async_write_ha_state = Mock()
            self._trigger_event = Mock()

        async def async_added_to_hass(self):
            pass

    class UpdateFailed(Exception):
        pass

    for name in ("homeassistant", "homeassistant.components", "homeassistant.helpers",
                 "homeassistant.util"):
        module(name)
    module("homeassistant.config_entries", ConfigEntry=object)
    module("homeassistant.core", HomeAssistant=object, callback=lambda fn: fn)
    module("homeassistant.helpers.device_registry", DeviceInfo=dict)
    module("homeassistant.helpers.update_coordinator", DataUpdateCoordinator=Coordinator,
           CoordinatorEntity=Entity, UpdateFailed=UpdateFailed)
    module("homeassistant.helpers.entity_platform", AddConfigEntryEntitiesCallback=object)
    module("homeassistant.components.event", EventEntity=type("EventEntity", (), {}))
    module("homeassistant.util.dt")
    module("pynhl", NHLApiError=type("NHLApiError", (Exception,), {}),
           NHLApiTimeoutError=type("NHLApiTimeoutError", (Exception,), {}),
           Plays=Mock(), Schedule=Mock())
    package = module("nhl_test_integration")
    package.__path__ = [str(ROOT)]

    def load(name):
        fullname = f"nhl_test_integration.{name}"
        spec = importlib.util.spec_from_file_location(fullname, ROOT / f"{name}.py")
        result = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, fullname, result)
        spec.loader.exec_module(result)
        return result

    load("const")
    load("goals")
    coordinator = load("coordinator")
    event = load("event")
    return coordinator, event, UpdateFailed


def test_shared_poll_delivers_once_and_recovers_without_replay(integration):
    coordinator_module, event_module, error = integration
    hass = SimpleNamespace(bus=SimpleNamespace(async_fire=Mock()))
    hass.async_add_executor_job = AsyncMock()
    coordinator = coordinator_module.NHLCoordinator(hass, "mtl", timedelta(seconds=2))
    entity = event_module.NHLGoalEvent(coordinator)

    async def poll(goal, state="LIVE"):
        hass.async_add_executor_job.return_value = ({
            "game_id": 1, "goal_event_id": goal, "goal_team_abbrev": "MTL",
            "game_state": state,
        }, "")
        result = await coordinator._async_update_data()
        entity._handle_coordinator_update()
        return result

    async def scenario():
        await poll(10)  # Baseline is not a new goal.
        hass.bus.async_fire.assert_not_called()
        entity._trigger_event.assert_not_called()
        await poll(11)
        hass.async_add_executor_job.assert_awaited_with(coordinator.get_game_data)
        hass.bus.async_fire.assert_called_once_with(
            "nhl_goal", {"team_abbrev": "MTL", "goal_tracked_team": True}
        )
        entity._trigger_event.assert_called_once_with("goal", {
            "game_id": 1, "goal_event_id": 11, "team_abbrev": "MTL",
            "goal_tracked_team": True, "tracked_team_abbrev": "MTL",
        })
        for _ in range(3):
            await poll(11, "FINAL")
        assert coordinator.update_interval == timedelta(seconds=2)
        hass.async_add_executor_job.side_effect = error("offline")
        with pytest.raises(error):
            await coordinator._async_update_data()
        coordinator.last_update_success = False
        entity._handle_coordinator_update()
        hass.async_add_executor_job.side_effect = None
        coordinator.last_update_success = True
        await poll(11, "FINAL")
        assert entity._trigger_event.call_count == 1
        assert hass.bus.async_fire.call_count == 1
        await poll(12, "FINAL")
        assert entity._trigger_event.call_count == 2
        await poll(12, "OFF")
        assert coordinator.update_interval == timedelta(seconds=600)
        await poll(12, "PRE")
        assert coordinator.update_interval == timedelta(seconds=10)

    asyncio.run(scenario())


def test_late_event_entity_does_not_replay_a_goal(integration):
    _, event_module, _ = integration
    coordinator = SimpleNamespace(goal_sequence=3, last_goal={"team_abbrev": "MTL"},
                                  last_update_success=True, team_abbrev="mtl", device_info={})
    entity = event_module.NHLGoalEvent(coordinator)
    coordinator.goal_sequence = 4
    asyncio.run(entity.async_added_to_hass())
    entity._handle_coordinator_update()
    entity._trigger_event.assert_not_called()
    coordinator.goal_sequence = 5
    entity._handle_coordinator_update()
    entity._trigger_event.assert_called_once()


def test_api_failure_is_update_failed(integration, monkeypatch):
    coordinator_module, _, error = integration
    monkeypatch.setattr(coordinator_module, "Schedule", Mock(
        side_effect=coordinator_module.NHLApiTimeoutError()
    ))
    coordinator = coordinator_module.NHLCoordinator(SimpleNamespace(), "mtl", timedelta(seconds=1))
    with pytest.raises(error, match="schedule"):
        coordinator.get_game_data()
