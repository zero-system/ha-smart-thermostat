# Smart Hybrid Heating Controller for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/zero-system/ha-smart-thermostat)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

A sophisticated Home Assistant custom component that intelligently manages hybrid heating systems, specifically designed for homes with both a mini-split heat pump and a pellet stove. This smart thermostat automatically selects the most efficient heating source based on environmental conditions, weather forecasts, and system performance.

## Features

- Intelligent switching between mini-split heat pump and pellet stove based on:
  - Outside temperature conditions
  - System heating performance
  - Weather forecasts
- Advanced pellet stove control with PID algorithm for precise temperature management
- Configurable heating modes (PID or ON/OFF)
- Predictive heating source selection using weather forecast data
- Real-time performance monitoring and heating source selection explanation
- Test interface for system behavior simulation

## Requirements

- Home Assistant installation
- Mini-split heat pump configured in Home Assistant
- Pellet stove with power and level controls configured in Home Assistant
- Temperature sensors for indoor and outdoor readings
- Weather integration for forecast data (optional but recommended)

## Installation

### HACS (Recommended)
1. Make sure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS:
   - Click the menu icon in the top right of HACS
   - Select "Custom repositories"
   - Add `https://github.com/zero-system/ha-smart-thermostat` with category "Integration"
3. Click "Download"
4. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/smart_thermostat` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

Configuration is handled through the UI:

1. Go to Settings > Devices & Services
2. Click "+ Add Integration"
3. Search for "Smart Thermostat"
4. Follow the configuration steps:
   - Select your mini-split entity
   - Select your pellet stove switches
   - Configure temperature sensors
   - Set minimum outside temperature threshold
   - Choose control mode (PID or ON/OFF)
   - Configure PID parameters if using PID mode

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## Issues and Feature Requests

Please use the [GitHub issue tracker](https://github.com/zero-system/ha-smart-thermostat/issues) to report any bugs or file feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially associated with any heat pump or pellet stove manufacturer.

[releases-shield]: https://img.shields.io/github/release/zero-system/ha-smart-thermostat.svg
[releases]: https://github.com/zero-system/ha-smart-thermostat/releases
[license-shield]: https://img.shields.io/github/license/zero-system/ha-smart-thermostat.svg