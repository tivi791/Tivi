import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
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
def generar_grafico(datos, titulo):
    categorias = list(datos.keys())
    valores = list(datos.values())

    # Normalizar los valores
    maximo = max(valores)
    valores_normalizados = [v / maximo * 100 if maximo != 0 else 0 for v in valores]

    # Ángulos para el gráfico radial
    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_normalizados += valores_normalizados[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores_normalizados, color='#1DB954', linewidth=2)
    ax.fill(angulos, valores_normalizados, color='#1DB954', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=12)
    ax.set_yticklabels([])
    ax.set_title(titulo, size=14, weight='bold', pad=20)

    # Guardamos el gráfico en un buffer para usarlo en HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
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
    for partida in partidas_hoy:
        for i, datos in enumerate(partida["datos"]):
            for k in datos:
                acumulado[roles[i]][k] += datos[k]

    # Generar informe en HTML
    html_contenido = f"<h2>Resumen Diario - {fecha_actual}</h2>"
    html_contenido += f"<p>Total de partidas hoy: {len(partidas_hoy)}</p>"

    for i, rol in enumerate(roles):
        datos = acumulado[rol]
        partidas_totales = len(partidas_hoy)
        promedio = {k: v / partidas_totales for k, v in datos.items()}
        maximos = list(promedio.values())

        # Agregar el gráfico
        grafico_buf = generar_grafico(promedio, f"Promedio del día - {rol}")
        grafico_base64 = base64.b64encode(grafico_buf.read()).decode('utf-8')

        html_contenido += f"<h3>{rol}</h3>"
        html_contenido += f"<img src='data:image/png;base64,{grafico_base64}' width='500'/>"
        html_contenido += f"<p><b>Análisis:</b> {generar_feedback(maximos)}</p>"

    st.markdown(html_contenido, unsafe_allow_html=True)
    # Opción para descargar el informe en formato HTML
    st.download_button(
        label="Descargar Informe en HTML",
        data=html_contenido,
        file_name="informe_honor_of_kings.html",
        mime="text/html"
    )
