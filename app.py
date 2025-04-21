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
    if usuario in usuarios_permitidos and usuarios_permitidos[usuario] == clave:
        return True
    return False

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
    
    # Añadir comentarios si la calificación es baja
    if calificacion == "Bajo":
        mensaje = f"Desempeño bajo. Requiere mejorar: {mensaje}"
    elif calificacion == "Promedio":
        mensaje = f"Desempeño promedio. Se recomienda mejorar: {mensaje}"
    elif calificacion == "Excelente":
        mensaje = f"Desempeño excelente. Buen trabajo: {mensaje}"
    
    return mensaje, calificacion

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.title("Honor of Kings - Registro Diario de Partidas y Análisis por Línea")

# Formulario de inicio de sesión
st.sidebar.header("Iniciar sesión")
usuario_ingresado = st.sidebar.text_input("Usuario")
clave_ingresada = st.sidebar.text_input("Contraseña", type="password")

# Botón de inicio de sesión
if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario_ingresado, clave_ingresada):
        st.session_state.autenticado = True
        st.sidebar.success("¡Has iniciado sesión correctamente!")
    else:
        st.sidebar.error("Usuario o contraseña incorrectos.")

# Si el usuario está autenticado, muestra el contenido de la app
if "autenticado" in st.session_state and st.session_state.autenticado:
    roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

    # Verifica si ya existe el estado de sesión para las partidas, si no lo inicializa
    if "registro_partidas" not in st.session_state:
        st.session_state.registro_partidas = []

    # Funciones de procesamiento de gráficos y retroalimentación
    def generar_grafico(datos, titulo, categorias, maximos):
        valores = list(datos.values())

        # Usamos el valor máximo de cada etiqueta para ajustar la escala
        valores_normalizados = [v / maximos[categoria] * 100 if maximos[categoria] != 0 else 0 for v, categoria in zip(valores, categorias)]

        N = len(categorias)
        angulos = [n / float(N) * 2 * pi for n in range(N)]
        valores_normalizados += valores_normalizados[:1]
        angulos += angulos[:1]

        # Crear el gráfico radial
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.plot(angulos, valores_normalizados, color='#007ACC', linewidth=2, label="Desempeño")
        ax.fill(angulos, valores_normalizados, color='#007ACC', alpha=0.3)
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, fontsize=12, fontweight='bold')
        ax.set_yticklabels([])  # Eliminamos las etiquetas en el eje Y
        ax.set_title(titulo, size=16, weight='bold', pad=20)
        ax.legend(loc='upper right')

        # Guardamos el gráfico en un buffer para usarlo en HTML
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return buf

    # Formulario de registro de partidas
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
        # Validación para que no se registre una partida vacía
        if all(d["Daño Infligido"] == 0 and d["Daño Recibido"] == 0 and d["Oro Total"] == 0 and d["Participación"] == 0 for d in jugadores):
            st.error("Por favor, complete todos los campos con datos válidos.")
        else:
            st.session_state.registro_partidas.append({
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "datos": jugadores.copy()
            })
            st.success("Partida guardada correctamente.")

    # Mostrar partidas guardadas
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
                if datos["Daño Infligido"] > 0 or datos["Daño Recibido"] > 0 or datos["Oro Total"] > 0 or datos["Participación"] > 0:
                    for k in datos:
                        acumulado[roles[i]][k] += datos[k]
                        if datos[k] > maximos[k]:
                            maximos[k] = datos[k]

        # Calcular los promedios
        total_partidas = len(partidas_hoy)
        for rol in roles:
            for k in acumulado[rol]:
                promedios_totales[k] += acumulado[rol][k]
        promedios_totales = {k: v / (total_partidas * len(roles)) for k, v in promedios_totales.items()}

        # Generar informe en HTML
                html_contenido = f"""
        <div style="background-color:#0f0f0f;padding:20px;border-radius:10px;border:2px solid #007ACC;color:white">
            <h2 style="color:#00C2FF;text-align:center;">WOLF SEEKERS E-SPORTS (LAS)</h2>
            <h3 style="color:#FFFFFF;text-align:center;">Resumen Diario - {fecha_actual}</h3>
            <p style="text-align:center;">Total de partidas hoy: <strong>{len(partidas_hoy)}</strong></p>
        """

        # Resumen general de todas las partidas
        for rol in roles:
            datos = acumulado[rol]
            if datos["Daño Infligido"] > 0 or datos["Daño Recibido"] > 0 or datos["Oro Total"] > 0 or datos["Participación"] > 0:
                promedio = {k: v / total_partidas for k, v in datos.items()}
                maximos_individuales = list(promedio.values())
                mensaje, calificacion = calificar_desempeno(maximos_individuales, rol)

                html_contenido += f"""
                <div style="margin-top:30px;padding:15px;border:1px solid #00C2FF;border-radius:8px;background-color:#1a1a1a;">
                    <h4 style="color:#00C2FF;">{rol}</h4>
                    <ul>
                        <li><strong>Daño Infligido Promedio:</strong> {promedio['Daño Infligido']:.2f}</li>
                        <li><strong>Daño Recibido Promedio:</strong> {promedio['Daño Recibido']:.2f}</li>
                        <li><strong>Oro Total Promedio:</strong> {promedio['Oro Total']:.2f}</li>
                        <li><strong>Participación Promedio:</strong> {promedio['Participación']:.2f}%</li>
                    </ul>
                    <p style="color:#FFD700;"><strong>Calificación:</strong> {calificacion}</p>
                    <p style="color:#CCCCCC;"><strong>Retroalimentación:</strong> {mensaje}</p>
                </div>
                """

        html_contenido += "</div>"

        st.markdown(html_contenido, unsafe_allow_html=True)
