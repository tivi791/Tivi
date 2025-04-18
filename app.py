import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
from datetime import datetime
import matplotlib.gridspec as gridspec
from fpdf import FPDF
import os

# Configuración
st.set_page_config(page_title="Honor of Kings - Análisis Diario", layout="wide")
st.title("📊 Análisis de Rendimiento Diario - Honor of Kings")

# Variables persistentes para almacenar partidas
if "partidas" not in st.session_state:
    st.session_state.partidas = []

roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# Generar gráfico radial

def generar_grafico(datos, titulo, maximos):
    categorias = list(datos.keys())
    valores = list(datos.values())
    valores_normalizados = [v / maximos[i] * 100 if maximos[i] != 0 else 0 for i, v in enumerate(valores)]

    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_normalizados += valores_normalizados[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.set_facecolor('#1c1c1c')
    fig.patch.set_facecolor('#0e1117')

    ax.plot(angulos, valores_normalizados, color='#1DB954', linewidth=2)
    ax.fill(angulos, valores_normalizados, color='#1DB954', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, color='white', fontsize=10)
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white', size=14, weight='bold', pad=10)
    return fig, valores_normalizados

# Feedback profesional

def generar_feedback(valores, rol):
    feedback = []
    dmg, rec, oro, part = valores[:4]
    
    if dmg > 80:
        feedback.append("• Daño infligido sobresaliente.")
    elif dmg < 40:
        feedback.append("• Daño bajo, mejorar posicionamiento.")

    if rec < 40:
        feedback.append("• Buena gestión defensiva.")
    elif rec > 80:
        feedback.append("• Recibe mucho daño, mejor defensa.")

    if oro > 70:
        feedback.append("• Excelente economía.")
    elif oro < 30:
        feedback.append("• Mal farmeo o control de mapa.")

    if part > 70:
        feedback.append("• Participación destacada.")
    elif part < 30:
        feedback.append("• Baja participación en equipo.")

    return "\n".join(feedback)

# Formulario de entrada de datos
st.header("📝 Ingreso de Datos de Partida")
jugadores = []

with st.form("form_datos"):
    for i, rol in enumerate(roles):
        st.subheader(f"{rol}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            dmg_inf = st.number_input(f"Daño Infligido ({rol})", min_value=0, key=f"dmg_inf_{i}")
        with col2:
            dmg_rec = st.number_input(f"Daño Recibido ({rol})", min_value=0, key=f"dmg_rec_{i}")
        with col3:
            oro = st.number_input(f"Oro Total ({rol})", min_value=0, key=f"oro_{i}")
        with col4:
            participacion = st.number_input(f"Participación (%) ({rol})", min_value=0.0, key=f"part_{i}")

        jugadores.append({
            "Daño Infligido": dmg_inf,
            "Daño Recibido": dmg_rec,
            "Oro Total": oro,
            "Participación": participacion
        })
    enviar = st.form_submit_button("Guardar Partida")

# Guardar partida actual en sesión
if enviar:
    hora = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.partidas.append({"hora": hora, "jugadores": jugadores})
    st.success(f"✅ Partida guardada a las {hora}")

# Mostrar total de partidas guardadas
st.info(f"📌 Total de partidas registradas hoy: {len(st.session_state.partidas)}")

# Generar PDF con todas las partidas del día
if st.button("📤 Generar Informe PDF del Día") and st.session_state.partidas:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    resumen_por_rol = {rol: [] for rol in roles}

    for partida in st.session_state.partidas:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Partida - {partida['hora']}", ln=True)

        maximos = []
        for k in partida['jugadores'][0].keys():
            max_val = max(j[k] for j in partida['jugadores'])
            maximos.append(max_val)

        for i, jugador in enumerate(partida['jugadores']):
            fig, valores_norm = generar_grafico(jugador, roles[i], maximos)
            feedback = generar_feedback(valores_norm, roles[i])
            resumen_por_rol[roles[i]].append(valores_norm)

            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png", dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_path = f"temp_{i}.png"
            with open(img_path, "wb") as f:
                f.write(img_buffer.read())

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{roles[i]}", ln=True)
            pdf.image(img_path, w=80)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 8, feedback)
            os.remove(img_path)

    # Página resumen con promedios
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "📊 Promedio del Día por Línea", ln=True)

    for rol in roles:
        datos = list(zip(*resumen_por_rol[rol]))
        promedios = [round(sum(e)/len(e), 2) for e in datos]
        feedback = generar_feedback(promedios, rol)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{rol}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, feedback)

    # Descargar PDF
    buffer_pdf = io.BytesIO()
    pdf.output(buffer_pdf)
    buffer_pdf.seek(0)

    st.download_button(
        label="📄 Descargar Informe del Día (PDF)",
        data=buffer_pdf,
        file_name="Informe_Honor_of_Kings.pdf",
        mime="application/pdf"
    )
