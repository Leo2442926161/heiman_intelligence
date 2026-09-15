"""Config flow for Heiman Intelligence with mDNS/zeroconf discovery (Shelly-like pattern)."""

from __future__ import annotations

import logging
from ipaddress import ip_address, ip_network
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    CONF_ARCHITECTURE,
    CONF_DEVICE_TYPE,
    CONF_MAC_ADDRESS,
    CONF_MODEL,
    DEFAULT_PORT,
    DEVICE_TYPES,
    DOMAIN,
)
from .helpers import info_value, normalize_identifier, normalize_mac

ConfigFlowResult = dict[str, Any]

_LOGGER = logging.getLogger(__name__)

_SKIP_DISCOVERY_NETS = (
    ip_network("127.0.0.0/8"),
    ip_network("169.254.0.0/16"),
    ip_network("172.17.0.0/16"),
    ip_network("172.18.0.0/16"),
    ip_network("172.19.0.0/16"),
    ip_network("172.20.0.0/16"),
    ip_network("172.21.0.0/16"),
)


def _usable_discovery_ip(value: str) -> bool:
    try:
        parsed = ip_address(value)
    except ValueError:
        return False
    if parsed.version != 4 or parsed.is_loopback or parsed.is_link_local or parsed.is_multicast:
        return False
    return not any(parsed in network for network in _SKIP_DISCOVERY_NETS)


def _discovery_attr(discovery_info: Any, key: str) -> Any:
    if isinstance(discovery_info, dict):
        return discovery_info.get(key)
    return getattr(discovery_info, key, None)


def _discovery_host(discovery_info: Any) -> tuple[str | None, bool]:
    candidates: list[Any] = []
    ip_addresses = _discovery_attr(discovery_info, "ip_addresses") or []
    if isinstance(ip_addresses, (list, tuple)):
        candidates.extend(ip_addresses)
    for key in ("ip_address", "host"):
        value = _discovery_attr(discovery_info, key)
        if value is not None:
            candidates.append(value)

    hostname = None
    for raw_host in candidates:
        if getattr(raw_host, "version", None) == 6:
            continue
        host = str(raw_host).strip("[]")
        try:
            parsed = ip_address(host)
        except ValueError:
            if hostname is None and host:
                hostname = host
            continue
        if parsed.version == 6:
            continue
        if _usable_discovery_ip(str(parsed)):
            return str(parsed), False
    if hostname:
        return hostname, False
    return None, False


def _discovery_port(discovery_info: Any) -> int:
    port = _discovery_attr(discovery_info, "port")
    if port in (None, ""):
        return DEFAULT_PORT
    try:
        return int(port)
    except (TypeError, ValueError):
        return DEFAULT_PORT


def _discovery_properties(discovery_info: Any) -> dict[str, Any]:
    properties = _discovery_attr(discovery_info, "properties")
    if isinstance(properties, dict):
        return dict(properties)
    return {}


class HeimanIntelligenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._port: int = DEFAULT_PORT
        self._mac: str | None = None
        self._model: str | None = None
        self._device_type: str | None = None
        self._device_name: str | None = None
        self._architecture: str | None = None
        self._info: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input.get(CONF_PORT, DEFAULT_PORT)
            return await self._async_try_connect()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
        )

    async def async_step_zeroconf(self, discovery_info: Any) -> ConfigFlowResult:
        host, is_ipv6 = _discovery_host(discovery_info)
        if is_ipv6:
            return self.async_abort(reason="ipv6_not_supported")
        if host is None:
            return self.async_abort(reason="cannot_connect")

        self._host = host
        self._port = _discovery_port(discovery_info)

        info = await self._async_get_info()

        if not info:
            return self.async_abort(reason="cannot_connect")

        self._set_info(info, _discovery_properties(discovery_info))
        if self._mac:
            await self.async_set_unique_id(self._mac)
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: self._host, CONF_PORT: self._port}
            )

        self.context["title_placeholders"] = {
            "name": self._device_name,
            "host": self._host,
        }

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self._async_create_entry()

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._device_name,
                "host": self._host,
                "model": self._model or "Unknown",
                "device_type": self._device_type or "Unknown",
            },
        )

    async def _async_try_connect(self) -> ConfigFlowResult:
        info = await self._async_get_info()

        if not info:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    }
                ),
                errors={"base": "cannot_connect"},
            )

        self._set_info(info)
        if self._mac:
            await self.async_set_unique_id(self._mac)
            self._abort_if_unique_id_configured()
        else:
            await self.async_set_unique_id(normalize_identifier(self._host))
            self._abort_if_unique_id_configured()

        return self._async_create_entry()

    async def _async_get_info(self) -> dict[str, Any]:
        if self._host is None:
            return {}

        ports: list[int] = []
        for port in (self._port, 8088, DEFAULT_PORT):
            try:
                value = int(port)
            except (TypeError, ValueError):
                continue
            if value not in ports:
                ports.append(value)

        last_error = ""
        for port in ports:
            device = None
            try:
                from .api import HeimanIntelligenceDevice

                device = HeimanIntelligenceDevice(host=self._host, port=port)
                info = await device.async_get_info(self.hass)
                if info:
                    self._port = port
                    return info
                last_error = device.last_error or last_error
            except Exception:
                _LOGGER.exception(
                    "Failed to load Heiman Intelligence info from %s:%s",
                    self._host,
                    port,
                )
            finally:
                if device is not None:
                    await device.close()
        if last_error:
            _LOGGER.debug(
                "No Heiman Intelligence /info from %s on ports %s: %s",
                self._host,
                ports,
                last_error,
            )
        return {}

    def _set_info(
        self,
        info: dict[str, Any],
        zeroconf_properties: dict[str, Any] | None = None,
    ) -> None:
        self._info = info
        props = zeroconf_properties or {}
        self._mac = normalize_mac(
            info_value(info, "mac", "macAddress")
            or props.get("mac")
            or props.get("id")
        )
        self._model = info_value(info, "model", "productModel") or "Unknown"
        self._device_name = info_value(info, "name", "deviceName") or "Heiman Device"
        raw_type = info_value(info, "deviceType", "type", "typeCode") or ""
        self._device_type = DEVICE_TYPES.get(
            str(raw_type).upper(), str(raw_type) or "unknown"
        )
        self._architecture = (
            info_value(info, "architecture", "networkArchitecture", "network")
            or props.get("arch")
            or "wifi"
        )

    def _async_create_entry(self) -> ConfigFlowResult:
        data = {
            CONF_HOST: self._host,
            CONF_PORT: self._port,
            CONF_MODEL: self._model or "Unknown",
            CONF_DEVICE_TYPE: self._device_type or "unknown",
            CONF_ARCHITECTURE: self._architecture or "wifi",
        }
        if self._mac:
            data[CONF_MAC_ADDRESS] = self._mac

        name = self._device_name or f"Heiman {self._model or 'Device'}"

        return self.async_create_entry(
            title=name,
            data=data,
        )
