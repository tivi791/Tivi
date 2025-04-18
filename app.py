import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from math import pi
import io
from datetime import datetime
import matplotlib.gridspec as gridspec
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Gráficos de Rendimiento", layout="wide")
st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/Honor_of_Kings_logo.png", width=120)
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
        font-size: 1em;
    }
</style>
""", unsafe_allow_html=True)

roles = ["🌟 TOPLANER", "🐉 JUNGLER", "🧠 MIDLANER", "🏹 ADCARRY", "🛡 SUPPORT"]

# Inicializar sesión
if "partidas" not in st.session_state:
    st.session_state.partidas = []

# Función para gráfico

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

# Feedback profesional
def generar_feedback(valores_norm):
    dmg, rec, oro, part = valores_norm[:4]
    feedback = []

    if dmg > 80:
        feedback.append("• Daño infligido sobresaliente.")
    elif dmg < 40:
        feedback.append("• Daño infligido bajo.")

    if rec < 40:
        feedback.append("• Buena gestión del daño.")
    elif rec > 80:
        feedback.append("• Exceso de daño recibido.")

    if oro > 70:
        feedback.append("• Economía sólida.")
    elif oro < 30:
        feedback.append("• Economía baja.")

    if part > 70:
        feedback.append("• Participación destacada.")
    elif part < 30:
        feedback.append("• Participación baja.")

    return "\n".join(feedback)

# Formulario
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
            dmg_inf = st.number_input(f"Daño Infligido {rol}", min_value=0, value=0, key=f"dmg_inf_{i}")
        with col2:
            dmg_rec = st.number_input(f"Daño Recibido {rol}", min_value=0, value=0, key=f"dmg_rec_{i}")
        with col3:
            oro = st.number_input(f"Oro Total {rol}", min_value=0, value=0, key=f"oro_{i}")
        with col4:
            participacion = st.number_input(f"Participación {rol} (%)", min_value=0, value=0, key=f"part_{i}")

        st.markdown("</div>", unsafe_allow_html=True)

        jugadores.append({
            "Daño Infligido": dmg_inf,
            "Daño Recibido": dmg_rec,
            "Oro Total": oro,
            "Participación": participacion
        })

    submit = st.form_submit_button("Guardar Partida")

# Guardar datos y generar PDF
if submit:
    maximos_globales = [max(j[metric] for j in jugadores) for metric in jugadores[0].keys()]
    partida = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "datos": jugadores,
        "graficos": [],
        "feedback": []
    }
    for i, jugador in enumerate(jugadores):
        fig, normalizados = generar_grafico(jugador, roles[i], maximos_globales)
        retro = generar_feedback(normalizados)
        partida["graficos"].append(fig)
        partida["feedback"].append((roles[i], retro))

    st.session_state.partidas.append(partida)
    st.success("Partida registrada correctamente.")

# Generar PDF del resumen diario
if st.session_state.partidas:
    if st.button("📄 Descargar Informe PDF del Día"):
        pdf_buffer = io.BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            for partida in st.session_state.partidas:
                plt.figure(figsize=(11, 8))
                plt.suptitle(f"Partida - {partida['hora']}", fontsize=16, color='white')
                fig = plt.gcf()
                fig.patch.set_facecolor('#0e1117')
                grid = gridspec.GridSpec(2, 3)

                for i, graf in enumerate(partida["graficos"]):
                    ax = plt.subplot(grid[i])
                    fig_tmp = graf
                    orig_ax = fig_tmp.get_axes()[0]
                    for line in orig_ax.get_lines():
                        ax.plot(line.get_xdata(), line.get_ydata(), color=line.get_color(), linewidth=2)
                    for patch in orig_ax.collections:
                        ax.fill(patch.get_paths()[0].vertices[:, 0], patch.get_paths()[0].vertices[:, 1], color=patch.get_facecolor()[0], alpha=0.3)
                    ax.set_xticks(orig_ax.get_xticks())
                    ax.set_xticklabels(orig_ax.get_xticklabels(), color='white')
                    ax.set_yticklabels([])
                    ax.set_title(roles[i], color='white', fontsize=10)
                pdf.savefig(bbox_inches='tight')
                plt.close()

                # Añadir retroalimentación
                plt.figure(figsize=(11, 8))
                fig = plt.gcf()
                fig.patch.set_facecolor('#0e1117')
                for i, (rol, feedback) in enumerate(partida['feedback']):
                    plt.text(0.05, 0.9 - i*0.18, f"{rol}", fontsize=12, color='#1DB954', weight='bold')
                    plt.text(0.05, 0.83 - i*0.18, feedback, fontsize=10, color='white')
                plt.axis('off')
                pdf.savefig(bbox_inches='tight')
                plt.close()

            # Promedios del día
            sumas = [{"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0} for _ in range(5)]
            for partida in st.session_state.partidas:
                for i, datos in enumerate(partida['datos']):
                    for k in datos:
                        sumas[i][k] += datos[k]

            totales = len(st.session_state.partidas)
            plt.figure(figsize=(11, 8))
            fig = plt.gcf()
            fig.patch.set_facecolor('#0e1117')
            plt.suptitle("Promedio Diario por Rol", fontsize=16, color='white')
            for i, suma in enumerate(sumas):
                promedio = {k: round(v / totales, 2) for k, v in suma.items()}
                texto = f"{roles[i]}\n" + "\n".join([f"{k}: {v}" for k, v in promedio.items()])
                plt.text(0.05, 0.9 - i*0.18, texto, fontsize=10, color='white')
            plt.axis('off')
            pdf.savefig(bbox_inches='tight')
            plt.close()

        st.download_button(
            label="📥 Descargar Informe PDF del Día",
            data=pdf_buffer.getvalue(),
            file_name="Informe_Honor_of_Kings.pdf",
            mime="application/pdf"
        )
