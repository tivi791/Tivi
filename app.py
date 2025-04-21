import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime
import subprocess

# Lista de usuarios permitidos (usuario: contraseña)
usuarios_permitidos = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}

# Función de autenticación
def autenticar_usuario(usuario, clave):
    return usuarios_permitidos.get(usuario) == clave

# Función para guardar y subir informe a GitHub
def guardar_informe_html(html_contenido):
    ruta_archivo = "informe_honor_of_kings.html"
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(html_contenido)

        # Configurar Git si no está configurado
        subprocess.run(["git", "config", "--global", "user.name", "AutoUploader"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "autobot@ejemplo.com"], check=True)

        # Agregar a staging
        subprocess.run(["git", "add", ruta_archivo], check=True)

        # Verificar si hay cambios nuevos
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff_check.returncode == 0:
            st.info("No hay cambios nuevos para subir a GitHub.")
            return

        # Commit y push
        commit_msg = f"Informe diario actualizado {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)

        st.success("Informe guardado y subido al repositorio GitHub correctamente.")
    except subprocess.CalledProcessError as e:
        st.warning(f"Error ejecutando un comando de Git: {e}")
    except Exception as e:
        st.warning(f"No se pudo subir el archivo a GitHub: {e}")

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.title("Honor of Kings - Registro Diario de Partidas y Análisis por Línea")

# Inicio de sesión
st.sidebar.header("Iniciar sesión")
usuario_ingresado = st.sidebar.text_input("Usuario")
clave_ingresada = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario_ingresado, clave_ingresada):
        st.session_state.autenticado = True
        st.sidebar.success("¡Has iniciado sesión correctamente!")
    else:
        st.sidebar.error("Usuario o contraseña incorrectos.")

if st.session_state.get("autenticado", False):
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

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.plot(angulos, valores_normalizados, color='#007ACC', linewidth=2)
        ax.fill(angulos, valores_normalizados, color='#007ACC', alpha=0.3)
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, fontsize=12, fontweight='bold')
        ax.set_yticklabels([])
        ax.set_title(titulo, size=16, weight='bold', pad=20)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return buf

    def generar_feedback(valores_norm):
        dmg, rec, oro, part = valores_norm[:4]
        fb = []
        if dmg > 80:
            fb.append("Daño infligido sobresaliente.")
        elif dmg < 40:
            fb.append("Daño infligido bajo.")
        if rec < 40:
            fb.append("Buena gestión del daño recibido.")
        elif rec > 80:
            fb.append("Exceso de daño recibido.")
        if oro > 70:
            fb.append("Economía sólida.")
        elif oro < 30:
            fb.append("Economía baja.")
        if part > 70:
            fb.append("Participación destacada.")
        elif part < 30:
            fb.append("Participación baja.")
        return " • ".join(fb)

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
            st.error("Por favor, completa todos los campos con datos válidos.")
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
        resumen_general = []
        maximos = {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0}
        promedios_totales = {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0}

        for partida in partidas_hoy:
            for i, datos in enumerate(partida["datos"]):
                for k in datos:
                    acumulado[roles[i]][k] += datos[k]
                    maximos[k] = max(maximos[k], datos[k])

        total_partidas = len(partidas_hoy)
        for rol in roles:
            for k in acumulado[rol]:
                promedios_totales[k] += acumulado[rol][k]
        promedios_totales = {k: v / (total_partidas * len(roles)) for k, v in promedios_totales.items()}

        html_contenido = f"<h2>Resumen Diario - {fecha_actual}</h2><p>Total de partidas hoy: {len(partidas_hoy)}</p>"

        for rol in roles:
            datos = acumulado[rol]
            promedio = {k: v / total_partidas for k, v in datos.items()}
            maximos_ind = list(promedio.values())
            categorias = list(promedio.keys())
            grafico_buf = generar_grafico(promedio, f"Promedio del día - {rol}", categorias, maximos)
            grafico_base64 = base64.b64encode(grafico_buf.read()).decode('utf-8')

            html_contenido += f"<h3>{rol}</h3><ul>"
            for k, v in promedio.items():
                html_contenido += f"<li><b>{k}:</b> {v:.2f}</li>"
            html_contenido += "</ul>"
            html_contenido += f"<img src='data:image/png;base64,{grafico_base64}' width='500'/>"
            html_contenido += f"<p><b>Análisis:</b> {generar_feedback(maximos_ind)}</p>"
            resumen_general.append(f"En {rol}, el rendimiento promedio fue: Daño Infligido: {promedio['Daño Infligido']:.2f}, Daño Recibido: {promedio['Daño Recibido']:.2f}, Oro Total: {promedio['Oro Total']:.2f}, Participación: {promedio['Participación']:.2f}")

        html_contenido += "<h3>Resumen General</h3><ul>"
        for item in resumen_general:
            html_contenido += f"<li>{item}</li>"
        html_contenido += "</ul>"

        st.markdown(html_contenido, unsafe_allow_html=True)

        guardar_informe_html(html_contenido)

        st.download_button(
            label="Descargar Informe en HTML",
            data=html_contenido,
            file_name="informe_honor_of_kings.html",
            mime="text/html"
        )
else:
    st.info("Por favor, inicia sesión para acceder al registro de partidas.")
