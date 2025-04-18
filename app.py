import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
from datetime import datetime
import matplotlib.gridspec as gridspec

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Gráficos de Rendimiento", layout="wide")
st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/Honor_of_Kings_logo.png", width=120)
st.title("Honor of Kings - Generador de Gráficos Radiales para eSports")
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #FFFFFF;
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #1DB954;
    }
    .feedback {
        background-color: #1c1c1c;
        padding: 1em;
        border-radius: 10px;
        margin-top: 1em;
        color: white;
        font-size: 1em;
        line-height: 1.5;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 1em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1a9d44;
    }
</style>
""", unsafe_allow_html=True)

roles = ["🌟 TOPLANER", "🐉 JUNGLER", "🧠 MIDLANER", "🏹 ADCARRY", "🛡 SUPPORT"]

# Función para generar gráfico radial con diseño profesional
def generar_grafico(datos, titulo, maximos):
    categorias = list(datos.keys())
    valores = list(datos.values())
    valores_normalizados = [v / maximos[i] * 100 if maximos[i] != 0 else 0 for i, v in enumerate(valores)]

    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_normalizados += valores_normalizados[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.set_facecolor('#1c1c1c')
    fig.patch.set_facecolor('#0e1117')

    ax.plot(angulos, valores_normalizados, color='#1DB954', linewidth=2)
    ax.fill(angulos, valores_normalizados, color='#1DB954', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, color='white', fontsize=13)
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white', size=16, weight='bold', pad=20)
    return fig, valores_normalizados

# Función para generar retroalimentación profesional
def generar_feedback(valores_norm, rol):
    feedback = [f"{rol}"]
    dmg, rec, oro, part = valores_norm[:4]

    if dmg > 80:
        feedback.append("• Daño infligido sobresaliente, gran presión en combate.")
    elif dmg < 40:
        feedback.append("• Daño infligido bajo, mejorar posicionamiento y toma de peleas.")

    if rec < 40:
        feedback.append("• Buena gestión del daño recibido.")
    elif rec > 80:
        feedback.append("• Exceso de daño recibido, mejora en decisiones defensivas.")

    if oro > 70:
        feedback.append("• Economía sólida, buen control de recursos.")
    elif oro < 30:
        feedback.append("• Economía baja, enfocar en farmeo y control de mapa.")

    if part > 70:
        feedback.append("• Participación destacada en objetivos y peleas.")
    elif part < 30:
        feedback.append("• Participación baja, integrarse más al juego en equipo.")

    return "\n".join(feedback)

jugadores = []
participaciones = []

with st.form("form_jugadores"):
    for i, rol in enumerate(roles):
        st.markdown(f"""
        <div style='background-color: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color:#1DB954;'>{rol}</h3>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            dmg_inf = st.number_input(f"Daño Infligido {rol} (mil)", min_value=0, value=0, key=f"dmg_inf_{i}")
        with col2:
            dmg_rec = st.number_input(f"Daño Recibido {rol} (mil)", min_value=0, value=0, key=f"dmg_rec_{i}")
        with col3:
            oro = st.number_input(f"Oro Total {rol} (mil)", min_value=0, value=0, key=f"oro_{i}")
        with col4:
            participacion = st.number_input(f"Participación {rol} (%)", min_value=0, value=0, key=f"part_{i}")  

        st.markdown("</div>", unsafe_allow_html=True)

        jugadores.append({
            "Daño Infligido": dmg_inf,
            "Daño Recibido": dmg_rec,
            "Oro Total": oro,
        })
        participaciones.append(participacion)

    submit = st.form_submit_button("Generar Gráficos")

if submit:
    for i in range(5):
        jugadores[i]["Participación"] = participaciones[i]

    maximos_globales = []
    for k in jugadores[0].keys():
        max_val = max(j[k] for j in jugadores)
        maximos_globales.append(max_val)

    st.subheader("Gráficos de Desempeño Individual")
    figs = []
    feedbacks = []

    for i, jugador in enumerate(jugadores):
        fig, valores_normalizados = generar_grafico(jugador, roles[i], maximos_globales)
        feedback = generar_feedback(valores_normalizados, roles[i])
        st.pyplot(fig)
        st.markdown(f"<div class='feedback'>{feedback}</div>", unsafe_allow_html=True)
        figs.append((fig, roles[i], feedback))

    fig_graficos = plt.figure(figsize=(15, 10), facecolor='#0e1117')
    spec = gridspec.GridSpec(3, 2, figure=fig_graficos)

    for i, (fig, rol, retro) in enumerate(figs):
        ax = fig_graficos.add_subplot(spec[i // 2, i % 2], polar=True)
        fig_axes = fig.get_axes()[0]
        for line in fig_axes.get_lines():
            ax.plot(line.get_xdata(), line.get_ydata(), color=line.get_color(), linewidth=2)
        for patch in fig_axes.collections:
            ax.fill(patch.get_paths()[0].vertices[:, 0], patch.get_paths()[0].vertices[:, 1], color=patch.get_facecolor()[0], alpha=0.3)
        ax.set_xticks(fig_axes.get_xticks())
        ax.set_xticklabels(fig_axes.get_xticklabels(), color='white', fontsize=12)
        ax.set_yticklabels([])
        ax.set_title(rol, color='white', fontsize=16)

    buf_graficos = io.BytesIO()
    fig_graficos.tight_layout()
    fig_graficos.savefig(buf_graficos, format="png", dpi=300, bbox_inches='tight')

    fig_descripciones = plt.figure(figsize=(15, 10), facecolor='#0e1117')
    spec = gridspec.GridSpec(3, 2, figure=fig_descripciones)

    for i, (fig, rol, retro) in enumerate(figs):
        ax = fig_descripciones.add_subplot(spec[i // 2, i % 2])
        ax.axis('off')
        ax.text(0.5, 0.95, f"{rol}", ha='center', va='top', color='#1DB954', fontsize=15, weight='bold')
        ax.text(0.5, 0.85, retro, ha='center', va='top', color='white', fontsize=12)

    buf_descripciones = io.BytesIO()
    fig_descripciones.tight_layout()
    fig_descripciones.savefig(buf_descripciones, format="png", dpi=300, bbox_inches='tight')

    st.download_button(
        label="📥 Descargar imagen con todos los gráficos",
        data=buf_graficos.getvalue(),
        file_name="Graficos_Honor_of_Kings.png",
        mime="image/png"
    )

    st.download_button(
        label="📥 Descargar imagen con todas las descripciones",
        data=buf_descripciones.getvalue(),
        file_name="Descripciones_Honor_of_Kings.png",
        mime="image/png"
    )
