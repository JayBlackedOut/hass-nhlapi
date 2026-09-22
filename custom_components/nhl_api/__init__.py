"""The NHL API integration."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ABBREV, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .coordinator import NHLCoordinator

PLATFORMS = [Platform.SENSOR, Platform.EVENT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NHL API from a config entry."""
    coordinator = NHLCoordinator(
        hass,
        entry.data[CONF_ABBREV].strip().lower(),
        timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        entry,
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload NHL API config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
