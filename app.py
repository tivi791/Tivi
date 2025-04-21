import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime

# Lista de usuarios permitidos (usuario: contraseña)
usuarios_permitidos = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}

# Función de autenticación
def autenticar_usuario(usuario, clave):
    return usuarios_permitidos.get(usuario) == clave

# Función para calificar el desempeño
def calificar_desempeno(valores_norm, rol):
    dmg, rec, oro, part = valores_norm[:4]
    calificacion = ""
    mensaje = ""

    if rol == "TOPLANER":
        if dmg < 60:
            mensaje = "Necesita mejorar el daño infligido."
            calificacion = "Bajo"
        elif dmg > 90:
            mensaje = "Excelente daño infligido."
            calificacion = "Excelente"
        if oro < 50:
            mensaje += " Necesita mejorar la economía."
            calificacion = "Bajo"
        if part < 50:
            mensaje += " Participación en peleas baja."
            calificacion = "Bajo"

    elif rol == "JUNGLER":
        if oro < 60:
            mensaje = "La economía podría mejorar."
            calificacion = "Promedio"
        if rec > 70:
            mensaje += " Daño recibido alto."
            calificacion = "Bajo"
        if part < 40:
            mensaje += " Participación en peleas baja."
            calificacion = "Bajo"

    elif rol == "MIDLANER":
        if dmg < 70:
            mensaje = "Daño infligido bajo."
            calificacion = "Bajo"
        if oro < 60:
            mensaje += " Economía por debajo del promedio."
            calificacion = "Promedio"
        if part < 50:
            mensaje += " Necesita participar más."
            calificacion = "Bajo"

    elif rol == "ADCARRY":
        if dmg < 80:
            mensaje = "Daño infligido bajo."
            calificacion = "Bajo"
        if rec > 60:
            mensaje += " Daño recibido alto."
            calificacion = "Bajo"

    elif rol == "SUPPORT":
        if oro < 30:
            mensaje = "Economía muy baja, aunque es normal para un support."
            calificacion = "Promedio"
        if part > 70:
            mensaje = "Excelente participación en peleas."
            calificacion = "Excelente"

    if calificacion == "Bajo":
        mensaje = f"Desempeño bajo. Requiere mejorar: {mensaje}"
    elif calificacion == "Promedio":
        mensaje = f"Desempeño promedio. Se recomienda mejorar: {mensaje}"
    elif calificacion == "Excelente":
        mensaje = f"Desempeño excelente. Buen trabajo: {mensaje}"

    return mensaje, calificacion

# Configuración de la página
st.set_page_config(page_title="WOLF SEEKERS - Análisis de Partidas", layout="wide")
st.markdown("""
    <style>
        .main, .stApp {
            background-color: #0a0a0a;
            color: #E0E0E0;
            font-family: 'Trebuchet MS', sans-serif;
        }
        .css-1v3fvcr {
            background-color: #0a0a0a;
        }
        h1, h2, h3, h4 {
            color: #00FFCC;
        }
        .stButton button {
            background-color: #00FFCC;
            color: black;
            font-weight: bold;
            border-radius: 10px;
        }
        .stTextInput > div > div > input {
            background-color: #1a1a1a;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🐺 WOLF SEEKERS E-SPORTS - Análisis de Partidas")

# Formulario de inicio de sesión
st.sidebar.header("🔐 Iniciar sesión")
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

    def generar_grafico(datos, titulo, categorias, maximos):
        valores = list(datos.values())
        valores_normalizados = [v / maximos[c] * 100 if maximos[c] != 0 else 0 for v, c in zip(valores, categorias)]

        N = len(categorias)
        angulos = [n / float(N) * 2 * pi for n in range(N)]
        valores_normalizados += valores_normalizados[:1]
        angulos += angulos[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angulos, valores_normalizados, color='#00FFCC', linewidth=2)
        ax.fill(angulos, valores_normalizados, color='#00FFCC', alpha=0.3)
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, color='white', fontsize=10, fontweight='bold')
        ax.set_yticklabels([])
        ax.set_title(titulo, color='#00FFCC', fontsize=14, weight='bold', pad=20)
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
        buf.seek(0)
        return buf

    st.header("📝 Registrar Nueva Partida")
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
                part = st.number_input(f"Participación (%) ({rol})", min_value=0, max_value=100, value=0, key=f"part_{i}")
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

    st.subheader("📊 Partidas Registradas Hoy")
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    partidas_hoy = [p for p in st.session_state.registro_partidas if p["fecha"] == fecha_actual]
    st.write(f"Total de partidas hoy: {len(partidas_hoy)}")

    if partidas_hoy:
        acumulado = {rol: {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0} for rol in roles}
        maximos = {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0}

        for partida in partidas_hoy:
            for i, datos in enumerate(partida["datos"]):
                for k in datos:
                    acumulado[roles[i]][k] += datos[k]
                    if datos[k] > maximos[k]:
                        maximos[k] = datos[k]

        total_partidas = len(partidas_hoy)

        for rol in roles:
            datos = acumulado[rol]
            if any(val > 0 for val in datos.values()):
                promedio = {k: v / total_partidas for k, v in datos.items()}
                categorias = list(promedio.keys())
                grafico_buf = generar_grafico(promedio, f"{rol} - Desempeño Promedio", categorias, maximos)
                b64_grafico = base64.b64encode(grafico_buf.getvalue()).decode('utf-8')
                mensaje, calificacion = calificar_desempeno(list(promedio.values()), rol)

                st.markdown(f"## {rol}")
                st.markdown(f"**Calificación:** {calificacion}")
                st.markdown(f"**Retroalimentación:** {mensaje}")
                st.image(f"data:image/png;base64,{b64_grafico}", use_column_width=True)
                st.markdown("---")
