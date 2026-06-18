import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as px
import plotly.express as cx
from vna_driver import PicoVNADriver, MockPicoVNA

st.set_page_config(page_title="PicoVNA HF Impedance Dashboard", layout="wide")

st.title("📡 PicoVNA High-Frequency Impedance Matching Dashboard")
st.write("Interface de contrôle et de visualisation pour l'adaptation d'impédance.")

# --- Sidebar Configuration ---
st.sidebar.header("🛠️ VNA Configurations")
use_mock = st.sidebar.checkbox("Use Mock VNA (Simulation Mode)", value=True)

start_f = st.sidebar.number_input("Start Frequency (MHz)", value=100.0, step=10.0)
stop_f = st.sidebar.number_input("Stop Frequency (MHz)", value=1000.0, step=10.0)
points = st.sidebar.slider("Number of Points", min_value=51, max_value=1001, value=201, step=50)
power = st.sidebar.slider("Output Power (dBm)", min_value=-40, max_value=10, value=-10, step=1)

# Session state initialization to hold data
if 'data' not in st.session_state:
    st.session_state.data = None

# --- Action Button ---
if st.sidebar.button("🚀 Run Measurement Sweep", use_container_width=True):
    with st.spinner("Connecting and sweeping instrument..."):
        # Instantiate correct driver
        vna = MockPicoVNA() if use_mock else PicoVNADriver()

        if vna.connect():
            vna.configure_sweep(start_f, stop_f, points, power)
            freqs, s11, s21 = vna.measure()
            vna.close()

            if freqs is not None:
                # Process data into a DataFrame
                df = pd.DataFrame({
                    'Frequency_Hz': freqs,
                    'Frequency_MHz': freqs / 1e6,
                    'S11_Real': np.real(s11),
                    'S11_Imag': np.imag(s11),
                    'S11_Mag_dB': 20 * np.log10(np.abs(s11) + 1e-9),
                    'S11_Phase_deg': np.angle(s11, deg=True),
                    'S21_Mag_dB': 20 * np.log10(np.abs(s21) + 1e-9),
                })
                st.session_state.data = df
                st.success("Measurement complete!")
            else:
                st.error("Measurement failed to capture data.")
        else:
            st.error("Could not establish connection to PicoVNA.")

# --- Main Dashboard Display ---
if st.session_state.data is not None:
    df = st.session_state.data

    # Key Metrics summary
    min_s11_idx = df['S11_Mag_dB'].idxmin()
    best_freq = df.loc[min_s11_idx, 'Frequency_MHz']
    min_s11_val = df.loc[min_s11_idx, 'S11_Mag_dB']

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Resonance / Min S11 Frequency", value=f"{best_freq:.2f} MHz")
    col2.metric(label="Min S11 Return Loss", value=f"{min_s11_val:.2f} dB")
    col3.metric(label="Data Points Collected", value=len(df))

    # Tabs for different plot types
    tab1, tab2 = st.tabs(["📊 Frequency Domain Plots (S11 / S21)", "🔮 Smith Chart (Impedance)"])

    with tab1:
        st.subheader("Magnitude Response")
        fig_mag = px.Figure()

        fig_mag.add_trace(
            px.Scatter(
                x=df['Frequency_MHz'],
                y=df['S11_Mag_dB'],
                mode='lines',
                name='S11'
            )
        )

        fig_mag.add_trace(
            px.Scatter(
                x=df['Frequency_MHz'],
                y=df['S21_Mag_dB'],
                mode='lines',
                name='S21'
            )
        )
        fig_mag.add_hline(y=-10, line_dash="dash", line_color="red", annotation_text="Standard -10dB Match Bound")
        st.plotly_chart(fig_mag, width='stretch')

        st.subheader("S11 Phase Response")
        import plotly.graph_objects as go

        fig_phase = px.Figure()

        fig_phase.add_trace(
            px.Scatter(
                x=df['Frequency_MHz'],
                y=df['S11_Phase_deg'],
                mode='lines',
                name='S11 Phase'
            )
        )
        st.plotly_chart(fig_phase, width='stretch')

    with tab2:
        st.subheader("Smith Chart Representation ($S_{11}$)")
        st.write("Used directly to calculate network matching components ($L$, $C$, stubs).")

        # Scat-plot on polar/smith format using Plotly's internal capabilities or standard structure
        # Plotly handles complex structures natively via specific layout setups or Scatterpolar
        fig_smith = go.Figure()

        # Add the S11 trace
        fig_smith.add_trace(go.Scatterpolar(
            r=np.sqrt(df['S11_Real'] ** 2 + df['S11_Imag'] ** 2),
            theta=df['S11_Phase_deg'],
            mode='lines+markers',
            name='S11 Path',
            text=[f"Freq: {f:.1f} MHz" for f in df['Frequency_MHz']],
            hoverinfo='text+r+theta'
        ))

        fig_smith.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 1], gridcolor="rgba(0,0,0,0.1)"),
                angularaxis=dict(showticklabels=True, direction="clockwise", period=360)
            ),
            showlegend=False,
            height=600
        )
        st.plotly_chart(fig_smith, width='stretch')

        # Export option
        st.download_button(
            label="💾 Export S-Parameter CSV Data",
            data=df.to_csv(index=False),
            file_name="picovna_measurement.csv",
            mime="text/csv"
        )
else:
    st.info("💡 Adjust configuration handles in the sidebar and press 'Run Measurement Sweep' to stream RF metrics.")