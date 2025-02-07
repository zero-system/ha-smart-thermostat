"""Constants for the Smart Thermostat integration."""

DOMAIN = "smart_thermostat"
PLATFORMS = ["climate"]

# Configuration constants
CONF_MINISPLIT_ENTITY = "minisplit_entity"
CONF_PELLET_POWER_SWITCH = "pellet_power_switch"
CONF_PELLET_LEVEL_SWITCHES = "pellet_level_switches"
CONF_OUTSIDE_TEMP_SENSOR = "outside_temp_sensor"
CONF_INSIDE_TEMP_SENSOR = "inside_temp_sensor"
CONF_MIN_OUTSIDE_TEMP = "min_outside_temp"
CONF_CONTROL_MODE = "control_mode"
CONF_PID_KP = "pid_kp"
CONF_PID_KI = "pid_ki"
CONF_PID_KD = "pid_kd"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_MIN_FORECAST_HOURS = "min_forecast_hours"

# Default values
DEFAULT_MIN_OUTSIDE_TEMP = 40  # °F
DEFAULT_PID_KP = 1.0
DEFAULT_PID_KI = 0.1
DEFAULT_PID_KD = 0.05
DEFAULT_MIN_FORECAST_HOURS = 2

# State attributes
ATTR_ACTIVE_SOURCE = "active_heating_source"
ATTR_SOURCE_REASON = "source_selection_reason"
ATTR_PELLET_LEVEL = "pellet_stove_level"
ATTR_OUTSIDE_TEMP = "outside_temperature"
ATTR_INSIDE_TEMP = "inside_temperature"
ATTR_TARGET_TEMP = "target_temperature"
ATTR_CONTROL_MODE = "control_mode"
ATTR_PID_OUTPUT = "pid_output"

# Heating sources
SOURCE_MINISPLIT = "mini_split"
SOURCE_PELLET = "pellet_stove"

# Control modes
MODE_PID = "pid"
MODE_ON_OFF = "on_off"

# Switch reasons
REASON_TEMP_TOO_LOW = "outside_temp_below_minimum"
REASON_TEMP_DECREASING = "inside_temp_decreasing"
REASON_NOT_REACHING_TARGET = "not_reaching_target"
REASON_WEATHER_FORECAST = "weather_forecast_unfavorable"
REASON_MANUAL = "manual_selection"

# Time constants
MONITOR_INTERVAL = 60  # seconds
TEMP_TREND_PERIOD = 900  # 15 minutes
TARGET_TIMEOUT = 1800  # 30 minutes
FORECAST_UPDATE_INTERVAL = 3600  # 1 hour

# Temperature constants
TEMP_CHANGE_THRESHOLD = 0.5  # °F
TEMP_TREND_SAMPLES = 5

# PID constants
PID_SAMPLE_TIME = 60  # seconds
PID_OUTPUT_LIMITS = (1, 5)  # Pellet stove levels

# Events
EVENT_SOURCE_CHANGED = "smart_thermostat_source_changed"
EVENT_LEVEL_CHANGED = "smart_thermostat_level_changed"