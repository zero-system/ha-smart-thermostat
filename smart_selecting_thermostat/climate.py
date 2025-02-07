"""Climate platform for smart thermostat."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_TENTHS,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_MINISPLIT_ENTITY,
    CONF_PELLET_POWER_SWITCH,
    CONF_PELLET_LEVEL_SWITCHES,
    CONF_OUTSIDE_TEMP_SENSOR,
    CONF_INSIDE_TEMP_SENSOR,
    CONF_MIN_OUTSIDE_TEMP,
    CONF_CONTROL_MODE,
    ATTR_ACTIVE_SOURCE,
    ATTR_SOURCE_REASON,
    SOURCE_MINISPLIT,
    SOURCE_PELLET,
    REASON_TEMP_TOO_LOW,
    REASON_TEMP_DECREASING,
    REASON_NOT_REACHING_TARGET,
    MODE_PID,
    MONITOR_INTERVAL,
    TEMP_TREND_PERIOD,
    TARGET_TIMEOUT,
)
from .pid_controller import PelletStovePIDController

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Smart Thermostat climate device."""
    async_add_entities([SmartThermostat(hass, config_entry)])

class SmartThermostat(ClimateEntity):
    """Smart thermostat with intelligent source selection."""

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the thermostat."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_name = "Smart Thermostat"
        self._attr_unique_id = config_entry.entry_id

        # Get configuration
        self._minisplit_entity = config_entry.data[CONF_MINISPLIT_ENTITY]
        self._pellet_power_switch = config_entry.data[CONF_PELLET_POWER_SWITCH]
        self._pellet_level_switches = config_entry.data[CONF_PELLET_LEVEL_SWITCHES]
        self._outside_temp_sensor = config_entry.data[CONF_OUTSIDE_TEMP_SENSOR]
        self._inside_temp_sensor = config_entry.data[CONF_INSIDE_TEMP_SENSOR]
        self._min_outside_temp = config_entry.data[CONF_MIN_OUTSIDE_TEMP]
        self._control_mode = config_entry.data[CONF_CONTROL_MODE]

        # State variables
        self._active_source = SOURCE_MINISPLIT
        self._source_reason = None
        self._hvac_mode = HVACMode.OFF
        self._target_temp = 20.0
        self._current_temp = None
        self._outside_temp = None
        self._temp_history = []
        self._last_target_change = datetime.now()

        # Set up PID controller if needed
        if self._control_mode == MODE_PID:
            self._pid_controller = PelletStovePIDController(
                config_entry.data.get("pid_kp", 1.0),
                config_entry.data.get("pid_ki", 0.1),
                config_entry.data.get("pid_kd", 0.05),
            )

        # Set up supported features
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.TURN_ON |
            ClimateEntityFeature.TURN_OFF
        )

        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
        self._attr_target_temperature_step = PRECISION_TENTHS
        self._attr_min_temp = 60
        self._attr_max_temp = 80

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Set up state change listeners
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [
                    self._inside_temp_sensor,
                    self._outside_temp_sensor,
                    self._minisplit_entity,
                    self._pellet_power_switch,
                ],
                self._async_state_changed,
            )
        )

        # Set up periodic monitoring
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._async_monitor_conditions,
                timedelta(seconds=MONITOR_INTERVAL),
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ACTIVE_SOURCE: self._active_source,
            ATTR_SOURCE_REASON: self._source_reason,
        }

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temp

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        return self._target_temp

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation ie. heat, cool, idle."""
        return self._hvac_mode

    @property
    def hvac_action(self) -> Optional[HVACAction]:
        """Return the current running hvac operation."""
        if self._hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if self._active_source == SOURCE_MINISPLIT:
            return HVACAction.HEATING
        return HVACAction.HEATING

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        self._target_temp = temp
        self._last_target_change = datetime.now()
        await self._async_control_heating()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self._async_turn_off_all()
        elif hvac_mode == HVACMode.HEAT and self._hvac_mode == HVACMode.OFF:
            await self._async_start_heating()
        self._hvac_mode = hvac_mode

    async def _async_control_heating(self) -> None:
        """Control the heating system based on current conditions."""
        if self._hvac_mode == HVACMode.OFF:
            return

        # Check conditions and select heating source
        await self._async_select_heating_source()

        if self._active_source == SOURCE_MINISPLIT:
            await self._async_control_minisplit()
        else:
            await self._async_control_pellet_stove()

    async def _async_select_heating_source(self) -> None:
        """Select the appropriate heating source based on conditions."""
        # Check outside temperature
        if self._outside_temp < self._min_outside_temp:
            if self._active_source != SOURCE_PELLET:
                self._active_source = SOURCE_PELLET
                self._source_reason = REASON_TEMP_TOO_LOW
                return

        # Check temperature trend if using mini-split
        if (
            self._active_source == SOURCE_MINISPLIT
            and len(self._temp_history) >= 2
        ):
            start_temp = self._temp_history[0]
            end_temp = self._temp_history[-1]
            if end_temp < start_temp:
                self._active_source = SOURCE_PELLET
                self._source_reason = REASON_TEMP_DECREASING
                return

        # Check if target temperature is being reached
        time_since_target_change = datetime.now() - self._last_target_change
        if (
            self._active_source == SOURCE_MINISPLIT
            and time_since_target_change.total_seconds() > TARGET_TIMEOUT
            and self._current_temp < self._target_temp
        ):
            self._active_source = SOURCE_PELLET
            self._source_reason = REASON_NOT_REACHING_TARGET
            return

    async def _async_control_minisplit(self) -> None:
        """Control the mini-split heat pump."""
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {
                "entity_id": self._minisplit_entity,
                "temperature": self._target_temp,
            },
            blocking=True,
        )

    async def _async_control_pellet_stove(self) -> None:
        """Control the pellet stove."""
        if self._control_mode == MODE_PID:
            # Update PID controller
            output = self._pid_controller.compute(
                self._current_temp, self._target_temp
            )
            await self._async_set_pellet_level(int(output))
        else:
            # Simple on/off control
            if self._current_temp < self._target_temp:
                await self._async_set_pellet_level(3)  # Medium power
            else:
                await self._async_set_pellet_level(1)  # Low power

    async def _async_set_pellet_level(self, level: int) -> None:
        """Set the pellet stove power level."""
        # Turn off all level switches
        for switch in self._pellet_level_switches:
            await self.hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": switch},
                blocking=True,
            )

        # Turn on the requested level
        if 1 <= level <= len(self._pellet_level_switches):
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": self._pellet_level_switches[level - 1]},
                blocking=True,
            )

    async def _async_turn_off_all(self) -> None:
        """Turn off all heating sources."""
        # Turn off mini-split
        await self.hass.services.async_call(
            "climate",
            "turn_off",
            {"entity_id": self._minisplit_entity},
            blocking=True,
        )

        # Turn off pellet stove
        await self.hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": self._pellet_power_switch},
            blocking=True,
        )

    async def _async_start_heating(self) -> None:
        """Start the heating system."""
        await self._async_select_heating_source()
        await self._async_control_heating()

    @callback
    async def _async_state_changed(self, event) -> None:
        """Handle state changes in monitored entities."""
        if event.data["entity_id"] == self._inside_temp_sensor:
            state = self.hass.states.get(self._inside_temp_sensor)
            if state is not None and state.state not in ("unknown", "unavailable"):
                self._current_temp = float(state.state)
                self._temp_history.append(self._current_temp)
                if len(self._temp_history) > TEMP_TREND_PERIOD:
                    self._temp_history.pop(0)

        elif event.data["entity_id"] == self._outside_temp_sensor:
            state = self.hass.states.get(self._outside_temp_sensor)
            if state is not None and state.state not in ("unknown", "unavailable"):
                self._outside_temp = float(state.state)

        await self._async_control_heating()

    @callback
    async def _async_monitor_conditions(self, now: datetime) -> None:
        """Periodic monitoring of conditions."""
        await self._async_control_heating()