"""Config flow for Smart Thermostat integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_MINISPLIT_ENTITY,
    CONF_PELLET_POWER_SWITCH,
    CONF_PELLET_LEVEL_SWITCHES,
    CONF_OUTSIDE_TEMP_SENSOR,
    CONF_INSIDE_TEMP_SENSOR,
    CONF_MIN_OUTSIDE_TEMP,
    CONF_CONTROL_MODE,
    CONF_PID_KP,
    CONF_PID_KI,
    CONF_PID_KD,
    DEFAULT_MIN_OUTSIDE_TEMP,
    DEFAULT_PID_KP,
    DEFAULT_PID_KI,
    DEFAULT_PID_KD,
)

class SmartThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Thermostat."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the inputs
            try:
                # Check if entities exist
                await self._validate_entities(self.hass, user_input)

                # Create the config entry
                return self.async_create_entry(title="Smart Thermostat", data=user_input,)

            except ValueError as err:
                errors["base"] = str(err)

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MINISPLIT_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate"),
                    ),
                    vol.Required(CONF_PELLET_POWER_SWITCH): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="switch"),
                    ),
                    vol.Required(CONF_PELLET_LEVEL_SWITCHES): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="switch",
                            multiple=True,
                        ),
                    ),
                    vol.Required(CONF_OUTSIDE_TEMP_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["sensor", "weather"],
                        ),
                    ),
                    vol.Required(CONF_INSIDE_TEMP_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor"),
                    ),
                    vol.Required(
                        CONF_MIN_OUTSIDE_TEMP,
                        default=DEFAULT_MIN_OUTSIDE_TEMP
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=-20,
                            max=100,
                            step=1,
                            unit_of_measurement="°F",
                        ),
                    ),
                    vol.Required(CONF_CONTROL_MODE, default="pid"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=["pid", "on_off"],
                            translation_key="control_mode",
                        ),
                    ),
                    # PID Parameters
                    vol.Optional(
                        CONF_PID_KP,
                        default=DEFAULT_PID_KP
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=0.1,
                        ),
                    ),
                    vol.Optional(
                        CONF_PID_KI,
                        default=DEFAULT_PID_KI
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=0.1,
                        ),
                    ),
                    vol.Optional(
                        CONF_PID_KD,
                        default=DEFAULT_PID_KD
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=0.1,
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def _validate_entities(self, hass: HomeAssistant, user_input: dict) -> None:
        """Validate that the entities exist."""
        # Check if mini-split entity exists
        if not hass.states.get(user_input[CONF_MINISPLIT_ENTITY]):
            raise ValueError("Mini-split entity not found")

        # Check if pellet stove power switch exists
        if not hass.states.get(user_input[CONF_PELLET_POWER_SWITCH]):
            raise ValueError("Pellet stove power switch not found")

        # Check if all level switches exist
        for switch in user_input[CONF_PELLET_LEVEL_SWITCHES]:
            if not hass.states.get(switch):
                raise ValueError(f"Pellet stove level switch {switch} not found")

        # Check if temperature sensors exist
        if not hass.states.get(user_input[CONF_OUTSIDE_TEMP_SENSOR]):
            raise ValueError("Outside temperature sensor not found")

        if not hass.states.get(user_input[CONF_INSIDE_TEMP_SENSOR]):
            raise ValueError("Inside temperature sensor not found")