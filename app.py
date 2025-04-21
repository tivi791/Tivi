import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
import pandas as pd
from datetime import datetime

# Lista de usuarios permitidos (usuario: contraseña)
usuarios_permitidos = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"} 

# Función de autenticación
def autenticar_usuario(usuario, clave):
    if usuario in usuarios_permitidos and usuarios_permitidos[usuario] == clave:
        return True
    return False

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

    def generar_feedback_por_rol(rol, valores_norm):
        # Desempeño por rol
        dmg, rec, oro, part = valores_norm[:4]
        fb = []

        if rol == "TOPLANER":
            if dmg > 80:
                fb.append("Daño infligido sobresaliente para el rol de Toplaner.")
            elif dmg < 40:
                fb.append("Daño infligido bajo, considera mejorar tu agresividad.")
            if rec > 70:
                fb.append("Excesivo daño recibido, intenta jugar más defensivo.")
            if part > 60:
                fb.append("Buena participación en peleas de equipo y objetivos.")
            elif part < 40:
                fb.append("Baja participación en peleas, intenta involucrarte más en las teamfights.")
        
        elif rol == "JUNGLER":
            if dmg > 70:
                fb.append("Daño infligido bueno para un Jungler, pero no olvides los objetivos.")
            if oro > 50:
                fb.append("Buena economía para un Jungler, ayuda en las rotaciones y ganks.")
            if part > 80:
                fb.append("Alta participación en peleas y objetivos, gran control del mapa.")
            elif part < 40:
                fb.append("Poca participación en peleas o objetivos, intenta ser más proactivo.")
        
        elif rol == "MIDLANER":
            if dmg > 80:
                fb.append("Gran daño infligido, muy buen control de la línea.")
            elif dmg < 50:
                fb.append("Daño infligido bajo, intenta aprovechar las rotaciones.")
            if part > 70:
                fb.append("Participación excelente en peleas de equipo.")
            elif part < 40:
                fb.append("Baja participación, debes rotar más y controlar la visión.")
        
        elif rol == "ADCARRY":
            if dmg > 90:
                fb.append("Daño sobresaliente, ¡tu presencia en peleas es vital!")
            elif dmg < 60:
                fb.append("Daño infligido bajo, intenta maximizar tu daño durante las peleas.")
            if oro > 70:
                fb.append("Excelente manejo de la economía, sigue así para obtener más daño.")
            if part > 60:
                fb.append("Buena participación en peleas, pero asegúrate de estar bien protegido por tu Support.")
        
        elif rol == "SUPPORT":
            if part > 80:
                fb.append("Gran participación en peleas y visión, mantienes a tu equipo a salvo.")
            if oro < 30:
                fb.append("Baja economía, pero el Support no necesita tanto oro, enfócate en la protección.")
            if dmg < 30:
                fb.append("Poco daño infligido, como Support no es una prioridad, pero trata de contribuir más.")
            if part < 50:
                fb.append("Baja participación en peleas, intenta involucrarte más en la protección de tu equipo.")
        
        return " • ".join(fb)

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
                for k in datos:
                    acumulado[roles[i]][k] += datos[k]
                    if datos[k] > maximos[k]:
                        maximos[k] = datos[k]

        # Calcular los promedios
        for rol in roles:
            for k in acumulado[rol]:
                promedios_totales[k] = acumulado[rol][k] / len(partidas_hoy)

        # Mostrar resumen general y retroalimentación
        for rol in roles:
            st.write(f"**Resumen de {rol}:**")
            st.write(f"Daño Infligido Promedio: {promedios_totales['Daño Infligido']}")
            st.write(f"Daño Recibido Promedio: {promedios_totales['Daño Recibido']}")
            st.write(f"Oro Promedio: {promedios_totales['Oro Total']}")
            st.write(f"Participación Promedio: {promedios_totales['Participación']}")
            st.write(f"**Retroalimentación:** {generar_feedback_por_rol(rol, [promedios_totales['Daño Infligido'], promedios_totales['Daño Recibido'], promedios_totales['Oro Total'], promedios_totales['Participación']])}")

    else:
        st.write("No se han registrado partidas hoy.")
