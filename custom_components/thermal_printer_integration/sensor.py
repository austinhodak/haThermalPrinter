"""Sensor platform for Thermal Printer integration."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Thermal Printer sensor."""
    printer = hass.data[DOMAIN][entry.entry_id]

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="thermal_printer",
        update_method=printer.update_status,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_refresh()

    async_add_entities([ThermalPrinterSensor(coordinator, printer)], True)


class ThermalPrinterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Thermal Printer sensor."""

    def __init__(self, coordinator, printer):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._printer = printer
        self._attr_name = "Thermal Printer Status"
        self._attr_unique_id = f"thermal_printer_{printer.ip_address}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._printer.state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            "ip_address": self._printer.ip_address,
            "last_updated": self._printer.last_updated,
        }
