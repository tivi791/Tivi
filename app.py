import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
from datetime import datetime
import matplotlib.gridspec as gridspec
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.title("Honor of Kings - Registro Diario de Partidas y Análisis por Línea")

roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

if "registro_partidas" not in st.session_state:
    st.session_state.registro_partidas = []

# Funciones de procesamiento
def generar_grafico(datos, titulo, maximos):
    categorias = list(datos.keys())
    valores = list(datos.values())
    valores_normalizados = [v / maximos[i] * 100 if maximos[i] != 0 else 0 for i, v in enumerate(valores)]

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
    return fig, valores_normalizados

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

    for i, rol in enumerate(roles):
        st.markdown(f"### {rol}")
        datos = acumulado[rol]
        partidas_totales = len(partidas_hoy)
        promedio = {k: v / partidas_totales for k, v in datos.items()}
        maximos = list(promedio.values())
        fig, valores_norm = generar_grafico(promedio, f"Promedio del día - {rol}", maximos)
        st.pyplot(fig)
        st.markdown(f"**Análisis:** {generar_feedback(valores_norm)}")

    df = []
    for partida in partidas_hoy:
        fila = {"Fecha": partida['fecha']}
        for i, datos in enumerate(partida['datos']):
            for k, v in datos.items():
                fila[f"{roles[i]} - {k}"] = v
        df.append(fila)

    df_final = pd.DataFrame(df)
    st.download_button("Descargar Resumen Diario (.csv)", data=df_final.to_csv(index=False), file_name="resumen_dia.csv", mime="text/csv")
