import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Honor of Kings - WOLF SEEKERS", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    body { background-color: #0a0a0a; color: white; }
    h1, h2, h3, h4, h5, h6 { color: #FFD700; font-family: 'Roboto', sans-serif; }
    .stButton>button {
        background-color: #FFD700; color: black;
        font-weight: bold; border-radius: 8px;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #1e1e1e; color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE USUARIOS ---
USUARIOS = {"Tivi": "2107", "Ghost": "203"}

# --- ROLES ---
ROLES = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# --- AUTENTICACIÓN ---
def autenticar(usuario, clave):
    return USUARIOS.get(usuario) == clave

# --- CALIFICACIÓN DE DESEMPEÑO ---
def calificar(promedio, rol, maximos):
    dmg, rec, oro, part = promedio.values()
    percentiles = {
        "Daño Infligido": dmg / maximos["Daño Infligido"] * 100 if maximos["Daño Infligido"] else 0,
        "Daño Recibido": rec / maximos["Daño Recibido"] * 100 if maximos["Daño Recibido"] else 0,
        "Oro Total": oro / maximos["Oro Total"] * 100 if maximos["Oro Total"] else 0,
        "Participación": part / maximos["Participación"] * 100 if maximos["Participación"] else 0,
    }

    reglas = {
        "TOPLANER": lambda d, o, p: (d >= 80 and o >= 60 and p >= 60),
        "JUNGLER": lambda d, o, p: (d >= 85 and o >= 70 and p >= 60),
        "MIDLANER": lambda d, o, p: (d >= 85 and o >= 70 and p >= 60),
        "ADCARRY": lambda d, o, p: (d >= 90 and o >= 70 and p >= 60),
        "SUPPORT": lambda d, o, p: (d >= 60 and o >= 50 and p >= 70),
    }

    evaluacion = reglas[rol](percentiles["Daño Infligido"], percentiles["Oro Total"], percentiles["Participación"])
    mensaje = "Excelente desempeño" if evaluacion else "Requiere mejorar"
    return mensaje, percentiles

# --- GRÁFICO RADAR ---
def graficar(promedio, titulo, maximos):
    categorias = list(promedio.keys())
    valores = [promedio[c] / maximos[c] * 100 if maximos[c] else 0 for c in categorias]
    valores += valores[:1]

    angulos = [n / float(len(categorias)) * 2 * pi for n in range(len(categorias))]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, color='#FFD700', linewidth=2)
    ax.fill(angulos, valores, color='#FFD700', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=12, color='white')
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white', pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#0a0a0a")
    buf.seek(0)
    return buf

# --- INTERFAZ DE USUARIO ---
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

# Autenticación
usuario = st.sidebar.text_input("Usuario")
clave = st.sidebar.text_input("Contraseña", type="password")
if st.sidebar.button("Iniciar sesión") and autenticar(usuario, clave):
    st.session_state["autenticado"] = True
    st.sidebar.success("Acceso concedido.")
elif "autenticado" not in st.session_state:
    st.warning("Debes iniciar sesión para continuar.")

# Página principal (si está autenticado)
if st.session_state.get("autenticado"):
    if "registro" not in st.session_state:
        st.session_state.registro = []

    with st.form("formulario_partida"):
        st.header("Registrar Nueva Partida")
        jugadores = []

        for i, rol in enumerate(ROLES):
            st.subheader(rol)
            cols = st.columns(4)
            dmg = cols[0].number_input(f"Daño Infligido ({rol})", min_value=0, key=f"dmg_{i}")
            rec = cols[1].number_input(f"Daño Recibido ({rol})", min_value=0, key=f"rec_{i}")
            oro = cols[2].number_input(f"Oro Total ({rol})", min_value=0, key=f"oro_{i}")
            part = cols[3].number_input(f"Participación (%) ({rol})", min_value=0, value=0, key=f"part_{i}")
            jugadores.append({"Daño Infligido": dmg, "Daño Recibido": rec, "Oro Total": oro, "Participación": part})

        if st.form_submit_button("Guardar Partida"):
            if all(sum(j.values()) == 0 for j in jugadores):
                st.error("Los datos están vacíos. Registra al menos una estadística.")
            else:
                st.session_state.registro.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "datos": jugadores
                })
                st.success("Partida guardada con éxito.")

    # RESUMEN DEL DÍA
    st.header("Resumen Diario")
    hoy = datetime.now().strftime("%Y-%m-%d")
    partidas_hoy = [p for p in st.session_state.registro if p["fecha"] == hoy]
    st.write(f"📅 Partidas registradas hoy: {len(partidas_hoy)}")

    if partidas_hoy:
        acumulado = {rol: {k: 0 for k in jugadores[0].keys()} for rol in ROLES}
        maximos = {k: 0 for k in jugadores[0].keys()}

        for partida in partidas_hoy:
            for i, stats in enumerate(partida["datos"]):
                for k, v in stats.items():
                    acumulado[ROLES[i]][k] += v
                    maximos[k] = max(maximos[k], v)

        for rol in ROLES:
            promedio = {k: acumulado[rol][k] / len(partidas_hoy) for k in acumulado[rol]}
            grafico = graficar(promedio, f"{rol} - Rendimiento", maximos)
            mensaje, percentiles = calificar(promedio, rol, maximos)

            st.subheader(f"{rol}")
            st.image(grafico, use_column_width=True)
            st.markdown(f"**Retroalimentación:** {mensaje}")
            st.markdown(
                f"- Daño: `{percentiles['Daño Infligido']:.1f}%` | "
                f"Oro: `{percentiles['Oro Total']:.1f}%` | "
                f"Participación: `{percentiles['Participación']:.1f}%`"
            )
else:
    st.stop()
