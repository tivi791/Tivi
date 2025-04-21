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
    dmg, rec, oro, part = valores_norm[:4]
    fb = []

    if rol == "TOPLANER":
        # Toplaner feedback
        if dmg < 50:
            fb.append("Daño infligido bajo. Asegúrate de aprovechar las oportunidades para hostigar al enemigo y aplicar presión en la línea.")
        elif dmg > 80:
            fb.append("Excelente daño infligido. Eres una fuente de presión importante en la línea.")
        
        if rec > 60:
            fb.append("Recibes mucho daño. Considera mejorar tu posicionamiento y buscar más apoyo de tu jungler.")
        elif rec < 40:
            fb.append("Buen manejo del daño recibido. Estás posicionándote bien para evitar ataques enemigos.")
        
        if oro < 60:
            fb.append("Tu oro es bajo. Necesitas mejorar el farmeo y buscar más oportunidades para obtener recursos.")
        elif oro > 80:
            fb.append("Buen control del oro. Estás maximizando tus recursos y lo que necesitas para tu construcción.")
        
        if part < 50:
            fb.append("Tu participación es baja. Necesitas estar más involucrado en las peleas y en los objetivos del equipo.")
        elif part > 70:
            fb.append("Excelente participación. Estás impactando las peleas de equipo y contribuyendo a los objetivos.")
    
    elif rol == "JUNGLER":
        # Jungler feedback
        if dmg < 60:
            fb.append("Daño infligido bajo. Considera mejorar tus rutas de jungla y buscar ganks más efectivos.")
        elif dmg > 80:
            fb.append("Buen daño infligido. Estás contribuyendo de manera significativa a las peleas y el control del mapa.")
        
        if rec > 60:
            fb.append("Excesivo daño recibido. Asegúrate de tener visión y evitar entrar en situaciones comprometidas sin el control adecuado.")
        
        if oro < 70:
            fb.append("Oro bajo. Aprovecha más los campamentos de la jungla y participa en los objetivos del mapa.")
        elif oro > 80:
            fb.append("Buen control de la jungla. Estás maximizando los recursos y participando bien en las rotaciones.")
        
        if part < 60:
            fb.append("Tu participación es baja. Como jungler, es esencial que estés presente en los momentos clave del juego.")
        elif part > 80:
            fb.append("Excelente participación. Estás impactando el mapa y asegurando los objetivos correctamente.")
    
    elif rol == "MIDLANER":
        # Midlane feedback
        if dmg < 60:
            fb.append("Tu daño infligido es bajo. Necesitas ser más agresivo y aprovechar las oportunidades para impactar las peleas.")
        elif dmg > 80:
            fb.append("Excelente daño infligido. Estás dominando tu rol y haciendo una gran presión en las peleas.")
        
        if rec > 50:
            fb.append("Daño recibido elevado. Asegúrate de tener control sobre tus rotaciones y posicionarte mejor.")
        
        if oro < 70:
            fb.append("Tu oro es bajo. Necesitas mejorar en el control de oleadas y en la gestión de tus recursos.")
        elif oro > 80:
            fb.append("Buen manejo del oro. Estás obteniendo recursos eficientemente para escalar en el juego.")
        
        if part < 60:
            fb.append("Tu participación es baja. Necesitas moverte por el mapa y participar más en las rotaciones.")
        elif part > 80:
            fb.append("Excelente participación. Tu control del mapa y tu impacto en peleas clave son notables.")
    
    elif rol == "ADCARRY":
        # ADC feedback
        if dmg < 60:
            fb.append("Daño infligido bajo. Como ADC, necesitas maximizar tu daño, especialmente en las peleas de equipo.")
        elif dmg > 80:
            fb.append("Excelente daño infligido. Estás siendo una gran fuente de daño en el juego tardío.")
        
        if rec > 50:
            fb.append("Recibes mucho daño. Es crucial que confíes en tu soporte y tengas un posicionamiento seguro.")
        
        if oro < 80:
            fb.append("Oro bajo. Necesitas mejorar en el farmeo y buscar más oportunidades para obtener recursos.")
        elif oro > 90:
            fb.append("Excelente control de oro. Estás maximizando tus recursos para llegar al final de la partida más fuerte.")
        
        if part < 50:
            fb.append("Tu participación es baja. Como ADC, deberías estar más involucrado en las peleas de equipo.")
        elif part > 70:
            fb.append("Excelente participación. Estás maximizando tu impacto en las peleas y contribuyendo al equipo.")
    
    elif rol == "SUPPORT":
        # Support feedback
        if dmg > 40:
            fb.append("Buen daño infligido para un soporte, pero recuerda que tu objetivo principal es proteger y asistir.")
        
        if rec > 50:
            fb.append("Recibes mucho daño. Asegúrate de mantenerte en una posición segura para proteger a tu ADC.")
        
        if oro < 60:
            fb.append("Oro bajo. Considera invertir más tiempo en ayudar a tu equipo y mejorar tu visión del mapa.")
        elif oro > 70:
            fb.append("Buen manejo del oro. Estás ayudando a tu equipo a obtener control de visión y objetos clave.")
        
        if part < 60:
            fb.append("Tu participación es baja. Como soporte, es fundamental que estés involucrado en las peleas y en el control de visión.")
        elif part > 80:
            fb.append("Excelente participación. Estás siendo un gran soporte en las peleas y ayudando a tu equipo con la visión.")
    
    return " • ".join(fb)
)

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
        total_partidas = len(partidas_hoy)
        for rol in roles:
            for k in acumulado[rol]:
                promedios_totales[k] += acumulado[rol][k]
        promedios_totales = {k: v / (total_partidas * len(roles)) for k, v in promedios_totales.items()}

        # Generar informe en HTML
        html_contenido = f"<h2>Resumen Diario - {fecha_actual}</h2>"
        html_contenido += f"<p>Total de partidas hoy: {len(partidas_hoy)}</p>"

        # Resumen general de todas las partidas
        for rol in roles:
            datos = acumulado[rol]
            promedio = {k: v / total_partidas for k, v in datos.items()}
            maximos_individuales = list(promedio.values())

            # Agregar el gráfico
            categorias = list(promedio.keys())
            grafico_buf = generar_grafico(promedio, f"Promedio del día - {rol}", categorias, maximos)
            grafico_base64 = base64.b64encode(grafico_buf.read()).decode('utf-8')

            # Agregar la información y el gráfico
            html_contenido += f"<h3>{rol}</h3>"
            html_contenido += f"<p><b>Datos:</b></p>"
            html_contenido += f"<ul>"
            for k, v in promedio.items():
                html_contenido += f"<li><b>{k}:</b> {v:.2f}</li>"
            html_contenido += f"</ul>"
            html_contenido += f"<img src='data:image/png;base64,{grafico_base64}' width='500'/>"
            html_contenido += f"<p><b>Análisis:</b> {generar_feedback(maximos_individuales)}</p>"

            # Resumen general de la partida
            resumen_general.append(f"En {rol}, el rendimiento promedio fue:")
            resumen_general.append(f"• Daño Infligido: {promedio['Daño Infligido']:.2f}")
            resumen_general.append(f"• Daño Recibido: {promedio['Daño Recibido']:.2f}")
            resumen_general.append(f"• Oro Total: {promedio['Oro Total']:.2f}")
            resumen_general.append(f"• Participación: {promedio['Participación']:.2f}")

        # Agregar análisis comparativo
        html_contenido += "<h3>Análisis Comparativo de Jugadores:</h3>"
        html_contenido += "<ul>"
        for rol in roles:
            html_contenido += f"<li><b>{rol}:</b> "
            promedio_individual = [acumulado[rol][k] / total_partidas for k in acumulado[rol]]
            for i, (k, promedio_valor) in enumerate(zip(acumulado[rol].keys(), promedio_individual)):
                if promedio_valor > promedios_totales[k]:
                    html_contenido += f"{k}: <span style='color: green;'>Por encima del promedio</span>, "
                else:
                    html_contenido += f"{k}: <span style='color: red;'>Por debajo del promedio</span>, "
            html_contenido += "</li>"
        html_contenido += "</ul>"

        # Mostrar resumen general al final
        html_contenido += "<h3>Resumen General de todas las partidas jugadas:</h3>"
        html_contenido += "<ul>"
        for item in resumen_general:
            html_contenido += f"<li>{item}</li>"
        html_contenido += "</ul>"

        st.markdown(html_contenido, unsafe_allow_html=True)

        # Opción para descargar el informe en formato HTML
        st.download_button(
            label="Descargar Informe en HTML",
            data=html_contenido,
            file_name="informe_honor_of_kings.html",
            mime="text/html"
        )
else:
    st.info("Por favor, inicia sesión para acceder al registro de partidas.")
