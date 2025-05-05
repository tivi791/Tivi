import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime
import os

# Lista de usuarios permitidos (usuario: contraseña)
usuarios_permitidos = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}

# Función de autenticación
def autenticar_usuario(usuario, clave):
    if usuario in usuarios_permitidos and usuarios_permitidos[usuario] == clave:
        return True
    return False

# Función para calificar el desempeño
def calificar_desempeno(valores_norm, rol, maximos):
    dmg, rec, oro, part = valores_norm[:4]
    calificacion = ""
    mensaje = ""

    percentil_dmg = (dmg / maximos['Daño Infligido']) * 100 if maximos['Daño Infligido'] != 0 else 0
    percentil_rec = (rec / maximos['Daño Recibido']) * 100 if maximos['Daño Recibido'] != 0 else 0
    percentil_oro = (oro / maximos['Oro Total']) * 100 if maximos['Oro Total'] != 0 else 0
    percentil_part = (part / maximos['Participación']) * 100 if maximos['Participación'] != 0 else 0

    # Ajuste de las reglas de calificación por rol
    reglas = {
        "TOPLANER": lambda dmg, oro, part: (dmg >= 60, oro >= 50, part >= 50),
        "JUNGLER": lambda dmg, oro, part: (dmg >= 70, oro >= 60, part >= 50),
        "MIDLANER": lambda dmg, oro, part: (dmg >= 70, oro >= 60, part >= 50),
        "ADCARRY": lambda dmg, oro, part: (dmg >= 80, oro >= 50, part >= 50),
        "SUPPORT": lambda dmg, oro, part: (dmg >= 50, oro >= 30, part >= 70)
    }

    if reglas[rol](dmg, oro, part):
        calificacion = "Excelente"
        mensaje = f"Excelente desempeño como {rol}."
    else:
        calificacion = "Bajo"
        mensaje = f"Necesita mejorar como {rol}."

    return mensaje, calificacion

# Función para generar gráficos
def generar_grafico(datos, titulo, categorias, maximos):
    valores = list(datos.values())
    valores_normalizados = [v / maximos[c] * 100 if maximos[c] != 0 else 0 for v, c in zip(valores, categorias)]

    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_normalizados += valores_normalizados[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores_normalizados, color='#FFD700', linewidth=2, label="Desempeño")
    ax.fill(angulos, valores_normalizados, color='#FFD700', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=12, fontweight='bold', color='white')
    ax.set_yticklabels([])
    ax.set_title(titulo, size=16, weight='bold', pad=20, color='white')
    ax.legend(loc='upper right')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    return buf

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.markdown("""
    <style>
        body { background-color: #0a0a0a; color: white; }
        h1, h2, h3, h4, h5, h6 { color: #FFD700; font-family: 'Roboto', sans-serif; }
        .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #1e1e1e; color: white; }
        .stNumberInput>div>div>input { background-color: #1e1e1e; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 WOLF SEEKERS E-SPORTS (LAS) - Registro Diario de Partidas")

# Autenticación de usuario
usuario_ingresado = st.sidebar.text_input("Usuario")
clave_ingresada = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario_ingresado, clave_ingresada):
        st.session_state.autenticado = True
        st.sidebar.success("¡Has iniciado sesión correctamente!")
    else:
        st.sidebar.error("Usuario o contraseña incorrectos.")

if "autenticado" in st.session_state and st.session_state.autenticado:
    roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

    if "registro_partidas" not in st.session_state:
        st.session_state.registro_partidas = []

    # Registro de partida
    st.header("Registrar Nueva Partida")
    jugadores = []

    with st.form("registro_form"):
        for i, rol in enumerate(roles):
            st.subheader(f"{rol}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                dmg = st.number_input(f"Daño Infligido ({rol})", min_value=0, key=f"dmg_{i}")
            with col2:
                rec = st.number_input(f"Daño Recibido ({rol})", min_value=0, key=f"rec_{i}")
            with col3:
                oro = st.number_input(f"Oro Total ({rol})", min_value=0, key=f"oro_{i}")
            with col4:
                part = st.number_input(f"Participación (%) ({rol})", min_value=0, value=0, key=f"part_{i}")
            jugadores.append({"Daño Infligido": dmg, "Daño Recibido": rec, "Oro Total": oro, "Participación": part})

        submit = st.form_submit_button("Guardar Partida")

    if submit:
        if all(d["Daño Infligido"] == 0 and d["Daño Recibido"] == 0 and d["Oro Total"] == 0 and d["Participación"] == 0 for d in jugadores):
            st.error("Por favor, complete todos los campos con datos válidos.")
        else:
            st.session_state.registro_partidas.append({
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "datos": jugadores.copy()
            })
            st.success("Partida guardada correctamente.")

    st.subheader("Partidas Registradas Hoy")
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    partidas_hoy = [p for p in st.session_state.registro_partidas if p["fecha"] == fecha_actual]
    st.write(f"Total de partidas hoy: {len(partidas_hoy)}")

    if partidas_hoy:
        acumulado = {rol: {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0} for rol in roles}
        maximos = {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0}
        promedios_totales = {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0}

        for partida in partidas_hoy:
            for i, datos in enumerate(partida["datos"]):
                if any(datos[k] > 0 for k in datos):
                    for k in datos:
                        acumulado[roles[i]][k] += datos[k]
                        if datos[k] > maximos[k]:
                            maximos[k] = datos[k]

        total_partidas = len(partidas_hoy)
        for rol in roles:
            for k in acumulado[rol]:
                promedios_totales[k] += acumulado[rol][k]
        promedios_totales = {k: v / (total_partidas * len(roles)) for k, v in promedios_totales.items()}

        html_contenido = f"<h2>Resumen Diario - {fecha_actual}</h2>"
        html_contenido += f"<p>Total de partidas hoy: {len(partidas_hoy)}</p>"
        html_contenido += f"<p>Equipo: <span style='color:#FFD700; font-weight:bold;'>WOLF SEEKERS E-SPORTS (LAS)</span></p>"

        for rol in roles:
            datos = acumulado[rol]
            if any(v > 0 for v in datos.values()):
                promedio = {k: v / total_partidas for k, v in datos.items()}
                categorias = list(promedio.keys())
                grafico_buf = generar_grafico(promedio, f"{rol} - Desempeño", categorias, maximos)

                img_html = f'<img src="data:image/png;base64,{base64.b64encode(grafico_buf.read()).decode()}" width="100%" />'
                html_contenido += f"<div><strong>{rol}</strong></div>"
                html_contenido += f"<div>{img_html}</div>"
                mensaje, calificacion = calificar_desempeno(list(promedio.values()), rol, maximos)
                html_contenido += f"<p><strong>Retroalimentación: </strong>{mensaje}</p>"

        st.markdown(html_contenido, unsafe_allow_html=True)

else:
    st.warning("Por favor, inicia sesión para continuar.")
