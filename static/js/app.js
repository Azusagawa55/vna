async function connect() {

    const response = await fetch("/connect");
    const data = await response.json();

    console.log("connect", data);

    alert(
        "Connected: " + data.connected +
        "\nStatus: " + (data.status ?? "n/a") +
        "\nHandle: " + (data.handle ?? "n/a") +
        (data.error ? "\nError: " + data.error : "")
    );

}


async function measure() {

    const response = await fetch("/measure");
    const data = await response.json();

    console.log("measure", data);

    if (data.error) {
        alert(data.error);
        return;
    }

    if (
        !Array.isArray(data.frequency) ||
        !Array.isArray(data.s11_logmag) ||
        !Array.isArray(data.s21_logmag) ||
        !Array.isArray(data.s12_logmag) ||
        !Array.isArray(data.s22_logmag) ||
        data.frequency.length === 0 ||
        data.frequency.length !== data.s11_logmag.length ||
        data.frequency.length !== data.s21_logmag.length ||
        data.frequency.length !== data.s12_logmag.length ||
        data.frequency.length !== data.s22_logmag.length
    ) {
        alert("No valid measurement data was returned by the instrument.");
        return;
    }

    Plotly.newPlot(
        "s11-plot",
        [{
            x: data.frequency,
            y: data.s11_logmag,
            type: "scatter",
            mode: "lines",
            name: "S11"
        }],
        {
            title: "S11 LogMag",
            xaxis: {
                title: "Frequency (Hz)"
            },
            yaxis: {
                title: "LogMag (dB)"
            }
        }
    );

    Plotly.newPlot(
        "s21-plot",
        [{
            x: data.frequency,
            y: data.s21_logmag,
            type: "scatter",
            mode: "lines",
            name: "S21"
        }],
        {
            title: "S21 LogMag",
            xaxis: {
                title: "Frequency (Hz)"
            },
            yaxis: {
                title: "LogMag (dB)"
            }
        }
    );

    Plotly.newPlot(
        "s12-plot",
        [{
            x: data.frequency,
            y: data.s12_logmag,
            type: "scatter",
            mode: "lines",
            name: "S12"
        }],
        {
            title: "S12 LogMag",
            xaxis: {
                title: "Frequency (Hz)"
            },
            yaxis: {
                title: "LogMag (dB)"
            }
        }
    );

    Plotly.newPlot(
        "s22-plot",
        [{
            x: data.frequency,
            y: data.s22_logmag,
            type: "scatter",
            mode: "lines",
            name: "S22"
        }],
        {
            title: "S22 LogMag",
            xaxis: {
                title: "Frequency (Hz)"
            },
            yaxis: {
                title: "LogMag (dB)"
            }
        }
    );

}

async function matching() {

    let response =
        await fetch("/matching");

    let data =
        await response.json();


    let txt =

        "Load Impedance\n\n" +

        "R = " + data.R + " Ω\n" +
        "X = " + data.X + " Ω\n\n" +

        "Matching Network\n\n" +

        "Q = " +
        data.network.Q + "\n" +

        data.network["Series Component"] +
        ": " +
        data.network["Series Value"] + "\n" +

        data.network["Parallel Component"] +
        ": " +
        data.network["Parallel Value"];


    alert(txt)

}
