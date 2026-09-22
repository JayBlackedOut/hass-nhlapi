"""Goal event entities for NHL teams."""

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import NHLCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a goal entity using the existing team poller."""
    async_add_entities([NHLGoalEvent(entry.runtime_data)])


class NHLGoalEvent(CoordinatorEntity[NHLCoordinator], EventEntity):
    """The last new goal observed in a tracked team's game."""

    _attr_has_entity_name = True
    _attr_name = "Goal"
    _attr_icon = "mdi:hockey-puck"
    _attr_event_types = ["goal"]

    def __init__(self, coordinator: NHLCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"nhl_{coordinator.team_abbrev}_goal"
        self._attr_device_info = coordinator.device_info
        self._goal_sequence = coordinator.goal_sequence

    async def async_added_to_hass(self) -> None:
        """Subscribe without replaying goals observed before this entity existed."""
        self._goal_sequence = self.coordinator.goal_sequence
        await super().async_added_to_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Publish each new goal once, without replaying on error recovery."""
        if (
            self.coordinator.last_update_success
            and self.coordinator.goal_sequence != self._goal_sequence
            and self.coordinator.last_goal is not None
        ):
            self._goal_sequence = self.coordinator.goal_sequence
            self._trigger_event("goal", dict(self.coordinator.last_goal))
        self.async_write_ha_state()
