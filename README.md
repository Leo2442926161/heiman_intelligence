<p align="center">

![HACS](https://img.shields.io/badge/HACS-Default-blue)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.7%2B-41BDF5)
![License](https://img.shields.io/badge/License-MIT-green)
</p>


---
<p align="left">
  <img src="custom_components/heiman_intelligence/brand/logo@2x.png" width="640">
</p>


# Heiman Intelligence 
Local Home Assistant integration for Heiman devices, gateways, and smart gateway hosts.


## Overview

Heiman Intelligence connects direct Wi-Fi devices, Heiman local gateways, and
Heiman smart gateway hosts to Home Assistant over the local network. It exposes
devices connected to a gateway and prediction results produced by local
computing as Home Assistant entities. The computing runs on the local host;
this integration reads its results and device state.



### Key Features

- Firmware update management
- Device diagnostics
- Battery monitoring
- Remote self-test
- Remote silence
- Home Assistant native entities
- HACS installation support

---

## Supported Devices

### Safety Devices
- Smoke Alarms
- Heat Alarms (Under Development)
- Carbon Monoxide Alarms (Planned)


### Gateways
- Smart RF Hub (**SubG RF radio only**)
- Smart Zigbee Gatewat(Planned)


---

## Installation

### HACS (Requires)
1. Click the icon and install Heiman Intelligence :
[![Install Heiman Intelligence ](https://community-assets.home-assistant.io/original/4X/8/c/d/8cd1e59d88b00047b1b5ef5e19611794f3699618.png)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Leo2442926161&repository=heiman_intelligence&category=integration)

2. Restart Home Assistant

---


## Configuration

Home Assistant communicates directly with the device on your local network using
HTTP and WebSocket. No Heiman account, cloud service, or authorization is needed.

1. Connect the Heiman device or gateway to the same local network as Home Assistant.
2. Open **Settings → Devices & services** in Home Assistant.
3. If Home Assistant discovers the device, select **Heiman Intelligence** under
   **Discovered** and confirm the device details. Discovery uses `heiman*` services
   on `_http._tcp.local.` or `_heiman._tcp.local.`.
4. If it is not discovered, select **Add integration**, search for
   **Heiman Intelligence**, and enter the device's IP address and port (80 by
   default). Home Assistant connects to the device and completes setup.

---



## Home Assistant Support

Compatible with:

- Home Assistant OS
- Home Assistant Container
- Home Assistant Supervised
- Home Assistant Core

---

## Community Driven

Many features were developed directly from feedback provided by Home Assistant users.

Current supported advanced features include:

- Remote Silence
- Remote Self-Test
- Device Diagnostics
- Siren Control
- Battery Status
- Tamper/Mount Detection
- OTA Upgrade Support

More features will continue to be added through future updates.


---

## How to Ask Questions

If you have questions, feature requests, or need help with setup, please open a GitHub Issue.

Before opening an issue, please include as much information as possible:

- Home Assistant version
- Heiman Intelligence  integration version
- Installation method, for example HACS or manual installation
- Device model
- Problem description
- Error logs, if available
- Screenshots, if helpful

Please avoid sharing sensitive information such as passwords, tokens, or account credentials.


[GitHub Issues Page](https://github.com/Leo2442926161/heiman_intelligence/issues)


---

## How to Contribute

Contributions are welcome.

You can help this project by:

- Reporting bugs
- Suggesting new features
- Improving documentation
- Testing new versions
- Submitting pull requests
- Sharing feedback from real Home Assistant usage

### Contributing Code

1. Fork this repository
2. Create a new branch
```bash
git checkout -b feature/your-feature-name
```

3. Make your changes
4. Test the integration locally
5. Commit your changes
6. git commit -m "Add your feature description"
7. Push your branch
```bash
git push origin feature/your-feature-name
```

8. Open a Pull Request

Please keep pull requests focused and describe clearly what has been changed.

---


## Support
Email: rd02@heiman.com.cn
