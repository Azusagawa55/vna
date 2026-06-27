from flask import Flask
from flask import jsonify
from flask import render_template
from pathlib import Path

from impedance import ImpedanceMatching
from pico_vna import PicoVNA

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "static"),
    template_folder=str(BASE_DIR / "templates")
)

vna = PicoVNA()
matcher = ImpedanceMatching()


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route("/connect")
def connect():
    # 1. Attempt to connect to the physical VNA hardware
    connection_result = vna.connect()

    # 2. If the connection is successful, load the calibration file into the DLL context
    if connection_result.get("connected"):
        # Replace this path with the actual location of your .cal file.
        cal_file_path = "./sdk/my_calibration_3ghz.cal"

        cal_result = vna.load_calibration(
            cal_file_path
        )

        # Append calibration status to your JSON response for easy debugging
        connection_result["calibration"] = cal_result
        connection_result["calibration_loaded"] = cal_result.get("success", False)
        if "error" in cal_result:
            connection_result["calibration_error"] = cal_result["error"]

    return jsonify(connection_result)


@app.route("/measure")
def measure():
    vna.configure_sweep(
        start_freq=1e6,
        stop_freq=3e9,
        n_points=201
    )

    data = vna.measure()

    return jsonify(data)


@app.route("/matching")
def matching():
    data = vna.measure()

    re = data["s11_real"][100]
    im = data["s11_imag"][100]

    impedance = matcher.gamma_to_impedance(
        re,
        im
    )

    network = matcher.calculate_l_network(
        impedance.real,
        impedance.imag,
        1e9
    )

    return jsonify({

        "R":
            round(
                impedance.real,
                2
            ),

        "X":
            round(
                impedance.imag,
                2
            ),

        "network":
            network

    })


if __name__ == "__main__":
    app.run(debug=True)
