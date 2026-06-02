import os
import sys
import time
import numpy as np

# Ensure we are on Windows for COM interface
if sys.platform == "win32":
    import win32com.client
else:
    print("Warning: PicoVNA COM API requires a Windows environment.")


class PicoVNADriver:
    def __init__(self):
        self.vna = None
        self.connected = False

    def connect(self):
        """Connects to the PicoVNA COM object."""
        try:
            # Initialize the COM connection to PicoVNA 2 or 3 depending on your version
            # Usually 'PicoVNA2.App' or 'PicoVNA3.App'
            self.vna = win32com.client.Dispatch("PicoVNA3.App")
            self.connected = True
            print("Successfully connected to PicoVNA.")
            return True
        except Exception as e:
            print(f"Error connecting to PicoVNA COM interface: {e}")
            self.connected = False
            return False

    def configure_sweep(self, start_freq_mhz, stop_freq_mhz, points=201, power_dbm=-10):
        """Configures the frequency sweep parameters."""
        if not self.connected:
            raise ConnectionError("VNA is not connected.")

        try:
            # Set frequencies (converted to Hz if required by the API, or MHz depending on version)
            # Most PicoVNA COM APIs accept Hz
            self.vna.SetStartFreq(start_freq_mhz * 1e6)
            self.vna.SetStopFreq(stop_freq_mhz * 1e6)
            self.vna.SetPoints(points)
            self.vna.SetPower(power_dbm)
            print(f"Sweep configured: {start_freq_mhz} MHz to {stop_freq_mhz} MHz, {points} points.")
        except Exception as e:
            print(f"Failed to configure sweep: {e}")

    def measure(self):
        """Triggers a single sweep and retrieves S-parameter data."""
        if not self.connected:
            raise ConnectionError("VNA is not connected.")

        try:
            # Trigger a single sweep step
            self.vna.Measure("Single")

            # Wait until measurement is finished
            while self.vna.IsMeasuring():
                time.time.sleep(0.1)

            # Retrieve data points
            points = int(self.vna.GetPoints())
            frequencies = np.array(self.vna.GetFreqList())  # in Hz

            # Fetch S11 and S21 as complex numbers or Real/Imag arrays
            # (Syntax varies slightly by Pico VNA SDK version; standard yields Real/Imag)
            s11_real = np.array(self.vna.GetS11("Real"))
            s11_imag = np.array(self.vna.GetS11("Imag"))
            s21_real = np.array(self.vna.GetS21("Real"))
            s21_imag = np.array(self.vna.GetS21("Imag"))

            s11 = s11_real + 1j * s11_imag
            s21 = s21_real + 1j * s21_imag

            return frequencies, s11, s21

        except Exception as e:
            print(f"Error during measurement: {e}")
            return None, None, None

    def close(self):
        """Closes the connection."""
        if self.vna:
            self.vna = None
            self.connected = False
            print("PicoVNA connection closed.")


# Mock class for testing on non-Windows systems or without hardware
class MockPicoVNA:
    def __init__(self):
        self.connected = True

    def connect(self): return True

    def configure_sweep(self, start, stop, points, power):
        self.start = start
        self.stop = stop
        self.points = points

    def measure(self):
        freqs = np.linspace(self.start * 1e6, self.stop * 1e6, self.points)
        # Simulate a simple resonant circuit / impedance match response
        center_f = (self.start + self.stop) * 1e6 / 2
        s11_mag = 0.1 + 0.8 * (1 - np.exp(-((freqs - center_f) / (center_f * 0.1)) ** 2))
        s11_phase = np.linspace(-np.pi, np.pi, self.points)
        s11 = s11_mag * np.exp(1j * s11_phase)
        s21 = (1 - s11_mag) * np.exp(-1j * s11_phase / 2)
        return freqs, s11, s21

    def close(self): pass