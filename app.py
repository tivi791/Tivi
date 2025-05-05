import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime

# ==================== CONFIGURACIÓN ==================== #

# Usuarios permitidos (usuario: contraseña)
USUARIOS_PERMITIDOS = {
    "Tivi": "2107",
    "Ghost": "203",
    "usuario3": "clave3"
}

ROLES = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# ==================== AUTENTICACIÓN ==================== #
def autenticar_usuario(usuario, clave):
    return USUARIOS_PERMITIDOS.get(usuario) == clave

# ==================== EVALUACIÓN DE DESEMPEÑO ==================== #
def calificar_desempeno(valores_norm, rol, maximos):
    dmg, rec, oro, part = valores_norm[:4]

    percentil = lambda v, m: (v / m) * 100 if m != 0 else 0

    percentil_dmg = percentil(dmg, maximos['Daño Infligido'])
    percentil_rec = percentil(rec, maximos['Daño Recibido'])
    percentil_oro = percentil(oro, maximos['Oro Total'])
    percentil_part = percentil(part, maximos['Participación'])

    reglas = {
        "TOPLANER": lambda d, o, p: (d >= 80 and o >= 60 and p >= 60),
        "JUNGLER": lambda d, o, p: (d >= 85 and o >= 70 and p >= 60),
        "MIDLANER": lambda d, o, p: (d >= 85 and o >= 70 and p >= 60),
        "ADCARRY": lambda d, o, p: (d >= 90 and o >= 70 and p >= 60),
        "SUPPORT": lambda d, o, p: (d >= 60 and o >= 50 and p >= 70)
    }

    if reglas[rol](percentil_dmg, percentil_oro, percentil_part):
        return (f"Excelente desempeño como {rol}. ¡Sigue así!", "Excelente", percentil_dmg, percentil_rec, percentil_oro, percentil_part)
    else:
        return (f"Requiere mejorar como {rol}. Considera optimizar estos puntos.", "Bajo", percentil_dmg, percentil_rec, percentil_oro, percentil_part)

# ==================== GENERACIÓN DE GRÁFICOS ==================== #
def generar_grafico(datos, titulo, categorias, maximos):
    valores = list(datos.values())
    valores_normalizados = [v / maximos[c] * 100 if maximos[c] else 0 for v, c in zip(valores, categorias)]

    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_normalizados += valores_normalizados[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores_normalizados, color='#FFD700', linewidth=2)
    ax.fill(angulos, valores_normalizados, color='#FFD700', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=12, fontweight='bold', color='white')
    ax.set_yticklabels([])
    ax.set_title(titulo, size=16, weight='bold', pad=20, color='white')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    return buf

# ==================== INTERFAZ ==================== #
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.markdown("""
    <style>
        body { background-color: #0a0a0a; color: white; }
        h1, h2, h3, h4, h5, h6 { color: #FFD700; font-family: 'Roboto', sans-serif; }
        .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border-radius: 8px; }
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background-color: #1e1e1e; color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 WOLF SEEKERS E-SPORTS (LAS) - Registro Diario de Partidas")

usuario = st.sidebar.text_input("Usuario")
clave = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario, clave):
        st.session_state.autenticado = True
        st.sidebar.success("¡Inicio de sesión exitoso!")
    else:
        st.sidebar.error("Credenciales incorrectas.")

if st.session_state.get("autenticado"):

    if "registro_partidas" not in st.session_state:
        st.session_state.registro_partidas = []

    st.header("Registrar Nueva Partida")

    jugadores = []
    with st.form("registro_form"):
        for i, rol in enumerate(ROLES):
            st.subheader(rol)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                dmg = st.number_input(f"Daño Infligido ({rol})", min_value=0, key=f"dmg_{i}")
            with col2:
                rec = st.number_input(f"Daño Recibido ({rol})", min_value=0, key=f"rec_{i}")
            with col3:
                oro = st.number_input(f"Oro Total ({rol})", min_value=0, key=f"oro_{i}")
            with col4:
                part = st.number_input(f"Participación (%) ({rol})", min_value=0, max_value=100, key=f"part_{i}")

            jugadores.append({"Daño Infligido": dmg, "Daño Recibido": rec, "Oro Total": oro, "Participación": part})

        if st.form_submit_button("Guardar Partida"):
            if all(all(v == 0 for v in j.values()) for j in jugadores):
                st.error("Completa todos los campos con datos válidos.")
            else:
                st.session_state.registro_partidas.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "datos": jugadores.copy()
                })
                st.success("Partida registrada correctamente.")

    st.subheader("Partidas Registradas Hoy")
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    partidas_hoy = [p for p in st.session_state.registro_partidas if p["fecha"] == fecha_actual]
    st.write(f"Total de partidas hoy: {len(partidas_hoy)}")

    if partidas_hoy:
        acumulado = {rol: {k: 0 for k in jugadores[0]} for rol in ROLES}
        maximos = {k: 0 for k in jugadores[0]}
        promedios_totales = {k: 0 for k in jugadores[0]}

        for partida in partidas_hoy:
            for i, datos in enumerate(partida["datos"]):
                for k in datos:
                    acumulado[ROLES[i]][k] += datos[k]
                    maximos[k] = max(maximos[k], datos[k])

        total_partidas = len(partidas_hoy)
        for rol in ROLES:
            for k in acumulado[rol]:
                promedios_totales[k] += acumulado[rol][k]

        promedios_totales = {k: v / (total_partidas * len(ROLES)) for k, v in promedios_totales.items()}

        html = f"<h2>Resumen Diario - {fecha_actual}</h2>"
        html += f"<p>Total de partidas hoy: {len(partidas_hoy)}</p>"
        html += "<p><strong>Equipo:</strong> <span style='color:#FFD700;'>WOLF SEEKERS E-SPORTS (LAS)</span></p>"

        for rol in ROLES:
            datos = acumulado[rol]
            if any(v > 0 for v in datos.values()):
                promedio = {k: v / total_partidas for k, v in datos.items()}
                categorias = list(promedio.keys())
                grafico = generar_grafico(promedio, f"{rol} - Desempeño", categorias, maximos)
                imagen = base64.b64encode(grafico.read()).decode()

                html += f"<h3>{rol}</h3>"
                html += f"<img src='data:image/png;base64,{imagen}' width='100%' />"

                mensaje, calificacion, p_dmg, p_rec, p_oro, p_part = calificar_desempeno(list(promedio.values()), rol, maximos)
                html += f"<p><strong>Retroalimentación:</strong> {mensaje}</p>"
                html += f"<p>Daño: {p_dmg:.1f}% | Oro: {p_oro:.1f}% | Participación: {p_part:.1f}%</p>"

        st.markdown(html, unsafe_allow_html=True)
else:
    st.warning("Por favor, inicia sesión para continuar.")
