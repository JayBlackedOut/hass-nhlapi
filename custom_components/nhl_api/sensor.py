"""NHL game status sensor, with legacy YAML support."""

from datetime import timedelta
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback, AddEntitiesCallback,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol

from .const import CONF_ABBREV, CONF_SCAN_INTERVAL, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL
from .coordinator import NHLCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ABBREV): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
})


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the legacy YAML sensor and compatibility goal events."""
    _LOGGER.warning(
        "Configuration of NHL API via configuration.yaml is deprecated and will be "
        "removed in version 2.0.0. Please migrate to the UI-based setup under "
        "Settings -> Devices & Services -> Add Integration -> NHL API."
    )
    interval = config.get(CONF_SCAN_INTERVAL, timedelta(seconds=DEFAULT_SCAN_INTERVAL))
    coordinator = NHLCoordinator(hass, config[CONF_ABBREV].strip().lower(), interval)
    await coordinator.async_refresh()
    async_add_entities([NHLSensor(coordinator)])


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor from the shared coordinator."""
    async_add_entities([NHLSensor(entry.runtime_data)])


class NHLSensor(CoordinatorEntity[NHLCoordinator], SensorEntity):
    """Representation of an NHL game."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:hockey-sticks"
    _attr_name = None

    def __init__(self, coordinator: NHLCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DEFAULT_NAME.lower()}_{coordinator.team_abbrev}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the game status or next game time."""
        return self.coordinator.data[1] if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return the latest game data."""
        return self.coordinator.data[0] if self.coordinator.data else {}
