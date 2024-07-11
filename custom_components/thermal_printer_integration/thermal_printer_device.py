"""Device class for Thermal Printer."""
import asyncio
from datetime import datetime, timedelta
from escpos.printer import Network
from escpos.exceptions import Error as PrinterError


class ThermalPrinterDevice:
    """Representation of a Thermal Printer device."""

    def __init__(self, hass, ip_address, port=9100):
        """Initialize the printer."""
        self.hass = hass
        self.ip_address = ip_address
        self.port = port
        self.printer = Network(self.ip_address, self.port)
        self.is_online = False
        self.last_updated = None

    async def print_content(self, content):
        """Print content on the thermal printer."""
        if not self.is_online:
            print("Printer is offline")
            return False

        try:
            await asyncio.to_thread(self._print, content)
            return True
        except PrinterError as e:
            print(f"Printer error: {str(e)}")
            await self.update_status()
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            await self.update_status()
            return False

    def _print(self, content):
        """Internal method to print content."""
        self.printer.text("\n")  # Start with a new line

        if content.startswith("QR:"):
            # Print QR code
            self.printer.qr(content[3:], size=8)
        else:
            # Print text content
            lines = content.split('\n')
            for line in lines:
                if line.startswith("# "):
                    # Large text for headers
                    self.printer.set(align='center', font='a', width=2, height=2)
                    self.printer.text(line[2:] + "\n")
                    self.printer.set(align='left', font='a', width=1, height=1)
                elif line.startswith("## "):
                    # Medium text for subheaders
                    self.printer.set(align='left', font='a', width=1, height=2)
                    self.printer.text(line[3:] + "\n")
                    self.printer.set(align='left', font='a', width=1, height=1)
                elif line.startswith("* "):
                    # Bullet points
                    self.printer.text("  • " + line[2:] + "\n")
                else:
                    # Regular text
                    self.printer.text(line + "\n")

        self.printer.text("\n")  # End with a new line
        self.printer.cut()

    async def update_status(self):
        """Update the online/offline status of the printer."""
        try:
            self.is_online = await self.hass.async_add_executor_job(self.printer.is_online)
        except Exception:
            self.is_online = False
        finally:
            self.last_updated = datetime.now()
        return self.is_online

    @property
    def state(self):
        """Return the state of the printer."""
        return "online" if self.is_online else "offline"

    @property
    def should_update(self):
        """Check if the printer status should be updated."""
        return self.last_updated is None or \
            datetime.now() - self.last_updated > timedelta(minutes=5)
