from flask import Flask
from flask import jsonify
from flask import render_template

from impedance import ImpedanceMatching
from pico_vna import PicoVNA

app = Flask(__name__)

vna = PicoVNA()
matcher = ImpedanceMatching()


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route("/connect")
def connect():
    return jsonify(
        vna.connect()
    )


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
