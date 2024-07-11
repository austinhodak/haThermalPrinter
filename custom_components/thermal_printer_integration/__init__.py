"""The Thermal Printer integration."""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .thermal_printer_device import ThermalPrinterDevice
from .const import DOMAIN

from .printer_templates import get_template

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Thermal Printer component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Thermal Printer from a config entry."""
    ip_address = entry.data["ip_address"]
    printer = ThermalPrinterDevice(hass, ip_address)
    hass.data[DOMAIN][entry.entry_id] = printer

    await printer.update_status()

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def print_service(call: ServiceCall):
        printer = hass.data[DOMAIN][entry.entry_id]
        content = call.data.get("content")
        template_name = call.data.get("template")
        template_data = call.data.get("data")

        if template_name:
            template = get_template(template_name)
            if template_data:
                content = template.format(**template_data)

        success = await printer.print_content(content)
        if not success:
            raise HomeAssistantError("Failed to print content")

    hass.services.async_register(DOMAIN, "print", print_service)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
