"""The Smart Thermostat Integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Thermostat from a config entry."""
    # Store an instance of the "domain" that you can access in your entities
    hass.data.setdefault(DOMAIN, {})

    # Create instance of your component and store it in hass.data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the climate platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener to track config entry updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload entities for this entry/domain
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove config entry from domain
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)