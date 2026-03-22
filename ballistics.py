import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(
    page_title="Ballistics Dynamics 3D",
    page_icon=Image.open("logo.png"),
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #000617;
    }
    header {
        background-color: rgba(0,0,0,0) !important;
    }
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono&display=swap');

    .main {
        background: radial-gradient(circle at top right, #2c2f48, #050508);
        color: #ffffff;
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(9, 1, 28, 0.95);
        border-right: 2px solid #3e3e4e;
    }
    [data-testid="stNumberInput"], [data-testid="stTextInput"], .stSelectbox, button {
        transition: all 0.3s ease-in-out !important;
        border-radius: 0px !important;
    }

    [data-testid="stNumberInput"]:hover, 
    .stMetric:hover, 
    button:hover {
        transform: translateY(-4px);
        border-color: #00f2ff !important;
        filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.6));
    }

    [data-testid="stNumberInput"] div[data-baseweb="input"] {
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 242, 255, 0.1) !important;
        background-color: rgba(0, 242, 255, 0.02) !important;
        border-radius: 0px !important;
    }

    [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
        border-color: #00f2ff !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.3) !important;
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 20px !important;
        border-radius: 16px;
        transition: all 0.3s ease;
    }

    h1 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #00f2ff, #0062ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        text-align: center;
        margin-bottom: 50px;
    }

    .stDataFrame {
        border: 1px solid #3e3e4e;
        border-radius: 8px;
    }
    
    p, label {
        font-family: 'Roboto Mono', monospace;
        color: #a0a0c0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Ballistic Modeling System")

if 'hist' not in st.session_state:
    st.session_state.hist = []
if 'a1' not in st.session_state:
    st.session_state.a1 = 45.0
if 'a2' not in st.session_state:
    st.session_state.a2 = 0.0

if 'hist' not in st.session_state:
    st.session_state.hist = []

st.sidebar.header("🚀 Primary Inputs")
env = st.sidebar.radio("Environment:", ("Vacuum", "Atmosphere"))
v = st.sidebar.number_input("Velocity (m/s):", value=60.0, format="%.2f", step=0.1)
a1 = st.sidebar.number_input("Elevation (deg):", value=st.session_state.a1, format="%.2f", step=0.1)
a2 = st.sidebar.number_input("Azimuth (deg):", value=st.session_state.a2, format="%.2f", step=0.1)
g = st.sidebar.number_input("Gravity (m/s²):", value=9.80665, format="%.4f", step=0.0001)

pr = st.sidebar.selectbox("Projectile Preset:", ["Custom", "Arrow", "Howitzer Shell", "Golf Ball", "Human Cannonball"])

prs = {
    "Arrow": {"m": 0.05, "cw": 0.02, "s": 0.00005},
    "Howitzer Shell": {"m": 40.0, "cw": 0.15, "s": 0.02},
    "Golf Ball": {"m": 0.045, "cw": 0.2, "s": 0.0014},
    "Human Cannonball": {"m": 80.0, "cw": 0.8, "s": 0.4},
    "Custom": {"m": 1.0, "cw": 0.47, "s": 0.01}
}

if env == "Atmosphere":
    st.sidebar.markdown("---")
    st.sidebar.header("🌍 Atmospheric Data")
    pd1 = prs[pr]
    if pr == "Custom":
        m = st.sidebar.number_input("Mass (kg):", value=pd1["m"], min_value=0.001, format="%.3f", step=0.01)
        cw = st.sidebar.number_input("Drag Coefficient:", value=pd1["cw"], min_value=0.001, format="%.3f", step=0.001)
        s = st.sidebar.number_input("Area (m²):", value=pd1["s"], min_value=0.00001, format="%.5f", step=0.00001)
    else:
        m, cw, s = pd1["m"], pd1["cw"], pd1["s"]
        st.sidebar.info(f"Mass: {m} kg | Cd: {cw} | Area: {s} m²")

    ro = st.sidebar.number_input("Air Density (kg/m³):", value=1.225, format="%.3f", step=0.001)
    st.sidebar.markdown("---")
    st.sidebar.header("🌀 External Forces")
    ws = st.sidebar.number_input("Wind Speed (m/s):", value=0.0, format="%.2f", step=0.1)
    wa = st.sidebar.slider("Wind Angle (deg):", -180, 180, 0, step=5, help="0=Tailwind, 90=Right, -90=Left, 180=Headwind")
    sp = st.sidebar.number_input("Spin (RPM):", value=0.0, format="%.0f", step=10.0)
    sa = st.sidebar.slider("Spin Angle (deg):", -180, 180, 0, step=5, help="0=Backspin, 90=Right, -90=Left, 180=Topspin")
else:
    m = cw = s = ro = ws = wa = sp = 1.0

st.sidebar.markdown("---")
st.sidebar.header("🎯 Targeting")
tx = st.sidebar.number_input("Distance (m):", value=100.0, format="%.2f")
tz = st.sidebar.number_input("Drift (m):", value=0.0, format="%.2f")
ty = st.sidebar.number_input("Altitude Y (m):", value=0.0, format="%.2f", help="Target height offset")

b1, b2, b3 = st.sidebar.columns(3)
fnd = b1.button("Find Angle")
sv = b2.button("Save")
clr = b3.button("Clear")

if clr:
    st.session_state.hist = []

def sim(ca, cz=0.0):
    xx, yy, zz, tt = [], [], [], []
    r1 = math.radians(ca)
    r2 = math.radians(cz)
    
    vx = v * math.cos(r1) * math.cos(r2)
    vy = v * math.sin(r1)
    vz = v * math.cos(r1) * math.sin(r2)
    
    if env == "Atmosphere":
        wr = math.radians(wa)
        wx, wz = ws * math.cos(wr), ws * math.sin(wr)
        t, x, y, z = 0.0, 0.0, 0.0, 0.0
        dt = 0.01
        hm = 0.0
        sar = math.radians(sa)

        while y >= min(0.0, ty - 10.0) and t < 1000:
            xx.append(x); yy.append(y); zz.append(z); tt.append(t)
            vrx, vry, vrz = vx - wx, vy, vz - wz
            vv = math.sqrt(vrx**2 + vry**2 + vrz**2)
            vh = math.sqrt(vrx**2 + vrz**2)
            
            r = ro * math.exp(-0.00012 * y)
            fd = 0.5 * cw * r * s * vv**2
            fl = 0.5 * (sp * 0.00001) * r * s * vv**2
            fly = fl * math.cos(sar)
            fll = fl * math.sin(sar)
            
            ax = -(fd * vrx / vv) / m if vv > 0 else 0
            ay = -g - (fd * vry / vv) / m if vv > 0 else -g
            az = -(fd * vrz / vv) / m if vv > 0 else 0
            ay += (fly * vh / vv) / m if vv > 0 else 0
            
            if vv > 0 and vh > 0:
                ax += (fll * (-vrz / vh) * (vh / vv)) / m
                az += (fll * (vrx / vh) * (vh / vv)) / m

            vx += ax * dt; vy += ay * dt; vz += az * dt
            x += vx * dt; y += vy * dt; z += vz * dt
            t += dt
            if y > hm: hm = y
        
        return xx, yy, zz, tt, math.sqrt(x**2 + z**2), hm, t, x, z

    else:
        y_end = min(0.0, ty - 10.0)
        if g != 0:
            D = vy**2 - 2 * g * y_end
            te = (vy + math.sqrt(D)) / g if D >= 0 else 0
        else:
            te = 0
        h = (vy**2) / (2 * g) if g != 0 else 0
        n = 100
        for i in range(n + 1):
            if te == 0: break
            ct = (te / n) * i
            xx.append(vx * ct)
            yy.append(vy * ct - 0.5 * g * ct**2)
            zz.append(vz * ct)
            tt.append(ct)
            
        fx = xx[-1] if xx else 0
        fz = zz[-1] if zz else 0
        dh = math.sqrt(fx**2 + fz**2)
        return xx, yy, zz, tt, dh, h, te, fx, fz

if fnd:
    with st.spinner("Calculating optimal 3D trajectory..."):
        ba, bz = 45.0, math.degrees(math.atan2(tz, tx))
        me = float('inf')
        def get_error(ta, t_az):
            xx, yy, zz, *_ = sim(ta, t_az)
            if not xx: return float('inf')
            return min(math.sqrt((x - tx)**2 + (y - ty)**2 + (z - tz)**2) for x, y, z in zip(xx, yy, zz))
        for ta in [x * 0.5 for x in range(1, 179)]:
            er = get_error(ta, bz)
            if er < me:
                me, ba = er, ta
        for _ in range(3):
            xx, yy, zz, *_ = sim(ba, bz)
            idx = min(range(len(xx)), key=lambda i: math.sqrt((xx[i] - tx)**2 + (yy[i] - ty)**2 + (zz[i] - tz)**2))
            cx, cz = xx[idx], zz[idx]
            if cx != 0:
                ea = math.degrees(math.atan2(tz, tx)) - math.degrees(math.atan2(cz, cx))
                bz += ea
            for ad in [-0.2, -0.1, 0, 0.1, 0.2]:
                ne = get_error(ba + ad, bz)
                if ne < me:
                    me, ba = ne, ba + ad

        a1, a2 = ba, bz
        if me > 5.0:
            st.toast(f"⚠️ Target out of reach! Best attempt: {me:.1f}m error.", icon="⚠️")
        else:
            st.toast(f"🎯 Target Locked! Elev={ba:.2f}°, Azi={bz:.2f}°", icon="🎯")
        st.session_state.a1 = float(ba)
        st.session_state.a2 = float(bz)
        st.rerun()

rx, ry, rz, rt, d, h, rte, rfx, rfz = sim(a1, a2)

if sv:
    st.session_state.hist.append({'x': rx, 'y': ry, 'z': rz, 'n': f"{pr} {a1:.1f}°/{a2:.1f}°"})

c1, c2, c3, c4 = st.columns(4)
c1.metric("FINAL X", f"{rfx:.2f} m")
c2.metric("APOGEE", f"{h:.2f} m")
c3.metric("FINAL Z (DRIFT)", f"{rfz:.2f} m")
c4.metric("FLIGHT TIME", f"{rte:.2f} s")

fig = go.Figure()
fig.add_trace(go.Scatter3d(x=rx, y=rz, z=ry, mode='lines', line=dict(color='#00f2ff', width=6), name='Active'))
fig.add_trace(go.Scatter3d(x=[tx], y=[tz], z=[ty], mode='markers', 
                          marker=dict(size=8, color='red', symbol='diamond'), name='Target'))

for i in st.session_state.hist:
    fig.add_trace(go.Scatter3d(x=i['x'], y=i['z'], z=i['y'], mode='lines', 
                               line=dict(width=3, dash='dot'), name=i['n']))

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    template="plotly_dark", height=700, margin=dict(l=0, r=0, t=0, b=0),
    scene=dict(
        bgcolor='rgba(0,0,0,0)', 
        xaxis_title="Distance X", 
        yaxis_title="Drift Z", 
        zaxis_title="Altitude Y",
        aspectratio=dict(x=2, y=1, z=1),
        xaxis=dict(
            backgroundcolor="rgba(0, 0, 0, 0)",
            gridcolor="#3e3e4e",
            showbackground=True
        ),
        yaxis=dict(
            backgroundcolor="rgba(0, 0, 0, 0)", 
            gridcolor="#3e3e4e",
            showbackground=True
        ),
        zaxis=dict(
            backgroundcolor="rgba(0, 0, 0, 0)", 
            gridcolor="#3e3e4e",
            showbackground=True
        )
    )
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("🔬 TELEMETRY DATA"):
    st.dataframe(pd.DataFrame({"Time": rt, "X": rx, "Y": ry, "Z": rz}), use_container_width=True)
