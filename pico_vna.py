import ctypes
import os
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent
sdk_path = str(BASE_DIR / "sdk")

os.add_dll_directory(sdk_path)

dll = ctypes.CDLL(
    os.path.join(
        sdk_path,
        "vna.dll"
    )
)


def logmag_db(value):
    gamma = np.sqrt(
        value.real ** 2 + value.imag ** 2
    )

    return float(
        20 * np.log10(
            gamma + 1e-12
        )
    )


class ComplexData(ctypes.Structure):
    _fields_ = [
        ("real", ctypes.c_double),
        ("imag", ctypes.c_double)
    ]


class MeasuredPoint(ctypes.Structure):
    _fields_ = [
        ("ref", ComplexData),
        ("meas", ComplexData)
    ]


class SParameterMeasurementPoint(ctypes.Structure):
    _fields_ = [
        ("measurement_mode", ctypes.c_int),
        ("measurement_point_index", ctypes.c_int),
        ("measurement_frequency_hz", ctypes.c_double),
        ("measurement_power_level_dbm", ctypes.c_double),
        ("measurement_bandwidth_hz", ctypes.c_double),
        ("forward", MeasuredPoint),
        ("reverse", MeasuredPoint),
        ("s11", ComplexData),
        ("s21", ComplexData),
        ("s12", ComplexData),
        ("s22", ComplexData),
        ("s11_uncorrected", ComplexData),
        ("s21_uncorrected", ComplexData),
        ("s12_uncorrected", ComplexData),
        ("s22_uncorrected", ComplexData),
        ("s11_raw", ComplexData),
        ("s21_raw", ComplexData),
        ("s12_raw", ComplexData),
        ("s22_raw", ComplexData),
        ("_reserved", ctypes.c_byte * 64)
    ]


class PicoVNA:

    def __init__(self):

        self.handle = ctypes.c_void_p()

        self.start_freq = 1e6
        self.stop_freq = 3e9
        self.n_points = 201
        self.power_level_dbm = 0.0
        self.bandwidth_hz = 1000.0

    def connect(self):

        try:

            if self.handle.value:
                return {

                    "connected": True,

                    "status": 0,

                    "handle": str(self.handle.value)
                }

            dll.vna_open_any.restype = ctypes.c_int
            dll.vna_open_any.argtypes = [
                ctypes.POINTER(ctypes.c_void_p)
            ]

            result = dll.vna_open_any(
                ctypes.byref(self.handle)
            )

            return {

                "connected": result == 0,

                "status": result,

                "handle": str(self.handle.value)
            }

        except Exception as e:

            return {

                "connected": False,

                "error": str(e)
            }

    def load_calibration(self, cal_file_path):
        """Loads a pre-saved PicoVNA .cal calibration file into the DLL engine."""
        if not self.handle.value:
            return {"error": "VNA must be connected before loading calibration"}

        try:
            # Check your SDK documentation for the exact string function variant
            # (Sometimes requires ctypes.c_char_p encoded to utf-8)
            dll.vna_load_calibration_file.argtypes = [
                ctypes.c_void_p,
                ctypes.c_char_p
            ]
            dll.vna_load_calibration_file.restype = ctypes.c_int

            path_bytes = cal_file_path.encode('utf-8')
            status = dll.vna_load_calibration_file(self.handle, path_bytes)

            return {"status": status, "success": status == 0}
        except AttributeError:
            return {"error": "Could not find calibration load function in vna.dll. Check SDK docs for exact name."}


    def configure_sweep(
            self,
            start_freq,
            stop_freq,
            n_points
    ):

        self.start_freq = start_freq
        self.stop_freq = stop_freq
        self.n_points = n_points

        return True

    def measure(self):

        try:

            if not self.handle.value:
                connect_result = self.connect()

                if not connect_result.get("connected"):
                    return {

                        "error": "VNA is not connected",

                        "connect": connect_result
                    }

            buffer = (SParameterMeasurementPoint * self.n_points)()

            # prepare sweep configuration

            dll.vna_create_frequency_sweep_configuration.argtypes = [

                ctypes.POINTER(ctypes.c_void_p),
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double
            ]

            dll.vna_create_frequency_sweep_configuration.restype = ctypes.c_int

            sweep = ctypes.c_void_p()
            create_status = dll.vna_create_frequency_sweep_configuration(

                ctypes.byref(sweep),
                ctypes.c_int(self.n_points),
                ctypes.c_double(self.start_freq),
                ctypes.c_double(self.stop_freq),
                ctypes.c_double(self.power_level_dbm),
                ctypes.c_double(self.bandwidth_hz)
            )

            if create_status != 0:
                return {

                    "error": "Failed to create VNA sweep configuration",

                    "status": int(create_status)
                }

            dll.vna_perform_measurement.argtypes = [

                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p
            ]

            dll.vna_perform_measurement.restype = ctypes.c_int

            result = dll.vna_perform_measurement(

                self.handle,
                sweep,
                ctypes.byref(buffer)
            )

            dll.vna_free_measurement_configuration.argtypes = [
                ctypes.c_void_p
            ]
            dll.vna_free_measurement_configuration.restype = None
            dll.vna_free_measurement_configuration(sweep)

            if result != 0:
                return {

                    "error": "VNA measurement failed",

                    "status": int(result)
                }

            frequencies = []

            s11_logmag = []
            s21_logmag = []
            s12_logmag = []
            s22_logmag = []

            real = []

            imag = []

            s21_real = []

            s21_imag = []

            s12_real = []

            s12_imag = []

            s22_real = []

            s22_imag = []

            for p in buffer:
                frequencies.append(
                    float(p.measurement_frequency_hz)
                )

                re = p.s11.real
                im = p.s11.imag

                real.append(float(re))
                imag.append(float(im))

                s11_logmag.append(
                    logmag_db(p.s11)
                )

                s21_re = p.s21.real
                s21_im = p.s21.imag

                s21_real.append(float(s21_re))
                s21_imag.append(float(s21_im))

                s21_logmag.append(
                    logmag_db(p.s21)
                )

                s12_re = p.s12.real
                s12_im = p.s12.imag

                s12_real.append(float(s12_re))
                s12_imag.append(float(s12_im))

                s12_logmag.append(
                    logmag_db(p.s12)
                )

                s22_re = p.s22.real
                s22_im = p.s22.imag

                s22_real.append(float(s22_re))
                s22_imag.append(float(s22_im))

                s22_logmag.append(
                    logmag_db(p.s22)
                )

            return {

                "frequency":
                    frequencies,

                "s11_logmag":
                    s11_logmag,

                "s22_logmag":
                    s22_logmag,

                "s21_logmag":
                    s21_logmag,

                "s12_logmag":
                    s12_logmag,

                "magnitude":
                    s11_logmag,

                "s22_magnitude":
                    s22_logmag,

                "s21_magnitude":
                    s21_logmag,

                "s12_magnitude":
                    s12_logmag,

                "s11_real":
                    real,

                "s11_imag":
                    imag,

                "s21_real":
                    s21_real,

                "s21_imag":
                    s21_imag,

                "s12_real":
                    s12_real,

                "s12_imag":
                    s12_imag,

                "s22_real":
                    s22_real,

                "s22_imag":
                    s22_imag,

                "status":
                    int(result)

            }

        except Exception as e:

            return {

                "error":
                    str(e)
            }
