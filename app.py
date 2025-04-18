import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import matplotlib.gridspec as gridspec

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Gráficos de Rendimiento", layout="wide")
st.title("Honor of Kings - Generador de Gráficos Radiales para eSports")
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #FFFFFF;
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
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

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
    ax.set_xticklabels(categorias, color='white')
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white', size=14)
    return fig, valores_normalizados

# Función para generar retroalimentación profesional
def generar_feedback(valores_norm, rol):
    feedback = []
    dmg, rec, oro, part = valores_norm[:4]  # Aseguramos que solo haya 4 valores

    # Retroalimentación según Daño Infligido
    if dmg > 80:
        feedback.append("Daño infligido alto.")
    elif dmg < 40:
        feedback.append("Daño infligido bajo.")

    # Retroalimentación según Daño Recibido
    if rec < 40:
        feedback.append("Buen control del daño recibido.")
    elif rec > 80:
        feedback.append("Demasiado daño recibido.")

    # Retroalimentación según Oro Total
    if oro > 70:
        feedback.append("Buena economía.")
    elif oro < 30:
        feedback.append("Economía baja.")

    # Retroalimentación según Participación
    if part > 70:
        feedback.append("Gran participación en equipo.")
    elif part < 30:
        feedback.append("Baja participación.")

    # Descripción general de cada rol
    feedback.append(f"Rol: {rol} - Importante para el control de los objetivos y la estrategia del equipo.")
    
    return "\n".join(feedback)

# Inputs por jugador
jugadores = []
participaciones = []

with st.form("form_jugadores"):
    for i, rol in enumerate(roles):
        st.subheader(f"{rol}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            dmg_inf = st.number_input(f"Daño Infligido {rol} (mil)", min_value=0, value=0, key=f"dmg_inf_{i}")
        with col2:
            dmg_rec = st.number_input(f"Daño Recibido {rol} (mil)", min_value=0, value=0, key=f"dmg_rec_{i}")
        with col3:
            oro = st.number_input(f"Oro Total {rol} (mil)", min_value=0, value=0, key=f"oro_{i}")
        with col4:
            participacion = st.slider(f"Participación {rol} (%)", min_value=0, max_value=100, value=0, key=f"part_{i}")

        jugadores.append({
            "Daño Infligido": dmg_inf,
            "Daño Recibido": dmg_rec,
            "Oro Total": oro,
        })
        participaciones.append(participacion)

    submit = st.form_submit_button("Generar Gráficos")

if submit:
    total_participacion = sum(participaciones)

    if total_participacion != 100:
        st.error("La suma de las participaciones debe ser 100% para poder graficar correctamente.")
    else:
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
            st.markdown(f"<div class='feedback'><b>Retroalimentación {roles[i]}:</b><br>{feedback}</div>", unsafe_allow_html=True)
            figs.append((fig, roles[i], feedback))

        # Crear figura compuesta para descarga
        fig_final = plt.figure(figsize=(15, 10), facecolor='#0e1117')  # Ajustar el tamaño de la figura
        spec = gridspec.GridSpec(3, 2, figure=fig_final)  # Cambiar la distribución de los gráficos

        for i, (fig, rol, retro) in enumerate(figs):
            ax = fig_final.add_subplot(spec[i // 2, i % 2], polar=True)
            fig_axes = fig.get_axes()[0]
            for line in fig_axes.get_lines():
                ax.plot(line.get_xdata(), line.get_ydata(), color=line.get_color(), linewidth=2)
            for patch in fig_axes.collections:
                ax.fill(patch.get_paths()[0].vertices[:, 0], patch.get_paths()[0].vertices[:, 1], color=patch.get_facecolor()[0], alpha=0.3)
            ax.set_xticks(fig_axes.get_xticks())
            ax.set_xticklabels(fig_axes.get_xticklabels(), color='white')
            ax.set_yticklabels([])
            ax.set_title(rol, color='white')

            # Ajustar posición del texto para que no se cruce
            ax.text(0.5, 1.1, retro, horizontalalignment='center', verticalalignment='center', color='white', fontsize=8, transform=ax.transAxes, wrap=True)

        # Guardar imagen como PNG
        buf = io.BytesIO()
        fig_final.tight_layout()
        fig_final.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button(
            label="📥 Descargar imagen con todos los gráficos y descripciones",
            data=buf.getvalue(),
            file_name="Graficos_Honor_of_Kings.png",
            mime="image/png"
        )
