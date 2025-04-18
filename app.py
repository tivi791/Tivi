import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

st.set_page_config(page_title="Honor of Kings - Análisis de Rendimiento", layout="wide")
st.title("📊 Honor of Kings - Análisis de Rendimiento por Rol")

roles = ["TOPLINE", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# Función para normalizar datos respecto a máximos globales
def normalizar_datos(valores, maximos_globales):
    return [v / m * 100 if m != 0 else 0 for v, m in zip(valores, maximos_globales)]

# Función para generar gráfico radial
def generar_grafico(valores, rol):
    categorias = ['Daño Infligido', 'Daño Recibido', 'Oro Total', 'Participación']
    valores += valores[:1]  # cerrar el gráfico
    categorias += categorias[:1]
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, linewidth=2, linestyle='solid', label=rol, color='gold')
    ax.fill(angles, valores, alpha=0.3, color='gold')
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontsize=10, color='white')
    ax.set_title(f"{rol}", fontsize=14, color='gold')
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    return fig

# Función para generar retroalimentación profesional
def generar_feedback(valores_norm):
    dmg, rec, oro, part = valores_norm
    feedback = []
    if dmg > 80:
        feedback.append("Alto impacto ofensivo, gran presión en el mapa.")
    elif dmg < 30:
        feedback.append("Bajo daño infligido, considerar rotaciones y mejor selección de enfrentamientos.")

    if rec > 80:
        feedback.append("Recibió mucho daño, posible mal posicionamiento o mal focus enemigo.")
    elif rec < 30:
        feedback.append("Buena evasión o posicionamiento estratégico.")

    if oro > 80:
        feedback.append("Gran eficiencia en farmeo y objetivos.")
    elif oro < 30:
        feedback.append("Bajo ingreso de oro, podría mejorar la eficiencia en la toma de recursos.")

    if part > 70:
        feedback.append("Alta participación en peleas, excelente coordinación.")
    elif part < 30:
        feedback.append("Baja participación, mejorar presencia en peleas clave.")

    return "\n".join(feedback)

# Entrada de datos
st.markdown("## Ingreso de Datos por Rol")

valores_roles = []
inputs = []

cols = st.columns(5)
for idx, rol in enumerate(roles):
    with cols[idx]:
        st.subheader(rol)
        dmg = st.number_input(f"Daño Infligido ({rol})", min_value=0, value=0)
        rec = st.number_input(f"Daño Recibido ({rol})", min_value=0, value=0)
        oro = st.number_input(f"Oro Total ({rol})", min_value=0, value=0)
        part = st.number_input(f"Participación ({rol}) (%)", value=0.0, format="%.1f")
        valores_roles.append([dmg, rec, oro, part])

# Normalización por máximos globales
valores_array = np.array(valores_roles)
maximos_globales = valores_array.max(axis=0)
valores_normalizados = [normalizar_datos(valores, maximos_globales) for valores in valores_roles]

# Mostrar gráficos y retroalimentación
st.markdown("## 📈 Gráficos y Retroalimentación por Rol")

figs = []
col_graficos = st.columns(5)

for idx, rol in enumerate(roles):
    with col_graficos[idx]:
        fig = generar_grafico(valores_normalizados[idx], rol)
        st.pyplot(fig)
        st.markdown(f"**Análisis Profesional - {rol}:**")
        st.markdown(generar_feedback(valores_normalizados[idx]))
        figs.append(fig)

# Opción para guardar gráficos
if st.button("📥 Descargar Gráficos como Imagen"):
    from PIL import Image
    import io

    ancho_total = 2500
    alto_total = 500
    imagen_final = Image.new('RGB', (ancho_total, alto_total), color=(14, 17, 23))

    for i, fig in enumerate(figs):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
        buf.seek(0)
        imagen = Image.open(buf)
        imagen_final.paste(imagen, (i * 500, 0))

    output_buf = io.BytesIO()
    imagen_final.save(output_buf, format='PNG')
    st.download_button(
        label="📸 Descargar Imagen de Gráficos",
        data=output_buf.getvalue(),
        file_name=f"graficos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )
