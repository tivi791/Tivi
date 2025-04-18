import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.title("Honor of Kings - Registro Diario de Partidas y Análisis por Línea")

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
