import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Configuración de la página
st.set_page_config(page_title="Análisis de Partida - Honor of Kings", layout="wide")
st.title("📊 Honor of Kings - Analizador de Partidas eSports")
st.markdown("Sube las estadísticas de cada línea y obtén gráficos + análisis profesional.")

# Colores por rol
role_colors = {
    "TOPLINE": "#1f77b4",
    "JUNGLE": "#ff7f0e",
    "MIDLINE": "#2ca02c",
    "ADCARRY": "#d62728",
    "SUPPORT": "#9467bd"
}

# Función para generar gráfico radar
def generar_grafico(jugador, valores, maximos):
    etiquetas = ['Daño Infligido', 'Daño Recibido', 'Oro Total', 'Participación']
    valores_normalizados = [v / m * 100 if m != 0 else 0 for v, m in zip(valores, maximos)]
    valores_normalizados += valores_normalizados[:1]

    angulos = np.linspace(0, 2 * np.pi, len(etiquetas), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angulos, valores_normalizados, color=role_colors[jugador], alpha=0.6)
    ax.plot(angulos, valores_normalizados, color=role_colors[jugador], linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiquetas)
    ax.set_title(jugador, size=16, color=role_colors[jugador])

    return fig

# Función para generar feedback basado en valores
feedback_tipos = {
    "Daño Infligido": ["poco daño", "daño medio", "excelente daño"],
    "Daño Recibido": ["fue muy vulnerable", "recibió daño moderado", "tanqueó correctamente"],
    "Oro Total": ["farmeó poco", "farmeó decentemente", "excelente farmeo"],
    "Participación": ["participación baja", "participación media", "presente en casi todas las jugadas"]
}

def generar_feedback(valores):
    etiquetas = ['Daño Infligido', 'Daño Recibido', 'Oro Total', 'Participación']
    feedback = []
    for i, valor in enumerate(valores):
        if valor < 33:
            fb = feedback_tipos[etiquetas[i]][0]
        elif valor < 66:
            fb = feedback_tipos[etiquetas[i]][1]
        else:
            fb = feedback_tipos[etiquetas[i]][2]
        feedback.append(f"{etiquetas[i]}: {fb}.")
    return feedback

# Formulario de entrada
datos = {}
roles = ["TOPLINE", "JUNGLE", "MIDLINE", "ADCARRY", "SUPPORT"]

st.markdown("---")
cols = st.columns(5)

for idx, rol in enumerate(roles):
    with cols[idx]:
        st.subheader(rol)
        daño = st.number_input(f"Daño Infligido {rol} (mil)", min_value=0, step=100)
        recibido = st.number_input(f"Daño Recibido {rol} (mil)", min_value=0, step=100)
        oro = st.number_input(f"Oro Total {rol} (mil)", min_value=0, step=100)
        participacion = st.number_input(f"Participación {rol} (%)", min_value=0.0, step=1.0, format="%.1f")
        datos[rol] = [daño, recibido, oro, participacion]

# Procesar datos
if st.button("Generar Gráficos y Feedback"):
    carpeta = "resultados"
    os.makedirs(carpeta, exist_ok=True)
    maximos = [max([datos[r][i] for r in roles]) for i in range(4)]

    figs = []
    feedbacks = []
    for rol in roles:
        fig = generar_grafico(rol, datos[rol], maximos)
        figs.append(fig)
        feedback = generar_feedback([v / m * 100 if m != 0 else 0 for v, m in zip(datos[rol], maximos)])
        feedbacks.append((rol, feedback))

    # Mostrar gráficos
    st.markdown("## 🎯 Resultados por Rol")
    cols = st.columns(5)
    for i, rol in enumerate(roles):
        with cols[i]:
            st.pyplot(figs[i])

    # Guardar gráficos y feedbacks como imagen
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    grafico_path = os.path.join(carpeta, f"graficos_{now}.png")
    feedback_path = os.path.join(carpeta, f"feedback_{now}.png")

    # Guardar imagen con gráficos
    fig_grid, axarr = plt.subplots(1, 5, figsize=(20, 5), subplot_kw=dict(polar=True))
    for i in range(5):
        valores = [v / m * 100 if m != 0 else 0 for v, m in zip(datos[roles[i]], maximos)]
        valores += valores[:1]
        angulos = np.linspace(0, 2 * np.pi, len(valores)-1, endpoint=False).tolist()
        angulos += angulos[:1]
        ax = axarr[i]
        ax.fill(angulos, valores, color=role_colors[roles[i]], alpha=0.6)
        ax.plot(angulos, valores, color=role_colors[roles[i]], linewidth=2)
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(['Daño', 'Recibido', 'Oro', 'Part'])
        ax.set_title(roles[i], size=14)
        ax.set_yticklabels([])
    plt.tight_layout()
    fig_grid.savefig(grafico_path)
    st.success("✅ Imagen de gráficos guardada")
    with open(grafico_path, "rb") as f:
        st.download_button("📥 Descargar Gráficos", f, file_name="graficos_partida.png")

    # Guardar imagen con feedback
    img = Image.new('RGB', (1000, 500), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    y = 20
    for rol, lines in feedbacks:
        draw.text((10, y), f"{rol}", fill=role_colors[rol], font=font)
        y += 20
        for line in lines:
            draw.text((30, y), f"- {line}", fill="black", font=font)
            y += 20
        y += 10
    img.save(feedback_path)
    with open(feedback_path, "rb") as f:
        st.download_button("📥 Descargar Feedback", f, file_name="feedback_partida.png")
