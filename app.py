from flask import Flask
from flask import jsonify
from flask import render_template

from pico_vna import PicoVNA

app = Flask(__name__)

vna = PicoVNA()


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


if __name__ == "__main__":
    app.run(debug=True)
