import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import datetime
import zipfile
import os

# Configuración de la página
st.set_page_config(page_title="Honor of Kings - Registro de Partidas", layout="wide")
st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/Honor_of_Kings_logo.png", width=120)
st.title("Honor of Kings - Registro de Partidas y Rendimiento")
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
    return fig

# Función para generar feedback
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

# Configurar el número de partidas
numero_partidas = st.number_input("¿Cuántas partidas quieres registrar?", min_value=1, max_value=20, value=7)

# Registrar los datos de las partidas
partidas = []
for partida_num in range(1, numero_partidas + 1):  # Ajustable según número de partidas
    partida_resultados = []
    st.subheader(f"Registro de Partida {partida_num}")
    for rol in roles:
        st.markdown(f"**{rol}**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            dmg_inf = st.number_input(f"Daño Infligido {rol} (mil)", min_value=0, value=0, key=f"dmg_inf_{partida_num}_{rol}")
        with col2:
            dmg_rec = st.number_input(f"Daño Recibido {rol} (mil)", min_value=0, value=0, key=f"dmg_rec_{partida_num}_{rol}")
        with col3:
            oro = st.number_input(f"Oro Total {rol} (mil)", min_value=0, value=0, key=f"oro_{partida_num}_{rol}")
        with col4:
            participacion = st.number_input(f"Participación {rol} (%)", min_value=0, max_value=100, value=0, key=f"part_{partida_num}_{rol}")
        
        partida_resultados.append({
            "Rol": rol,
            "Daño Infligido": dmg_inf,
            "Daño Recibido": dmg_rec,
            "Oro Total": oro,
            "Participación": participacion,
        })

    partidas.append(partida_resultados)

submit = st.button("Generar Gráficos y Registro Final")

# Generar los gráficos y resúmenes
if submit:
    for partida_num, partida_resultados in enumerate(partidas):
        maximos_globales = [max(jugador[metric] for jugador in partida_resultados) for metric in ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]]
        st.subheader(f"Gráficos de la Partida {partida_num + 1}")
        
        for jugador in partida_resultados:
            fig = generar_grafico(jugador, jugador["Rol"], maximos_globales)
            st.pyplot(fig)

    # Generar el resumen global
    st.subheader("Resumen Final de las Partidas")
    resumen_global = {}

    for partida_num, partida_resultados in enumerate(partidas):
        for jugador in partida_resultados:
            if jugador["Rol"] not in resumen_global:
                resumen_global[jugador["Rol"]] = {"Total Daño": 0, "Total Oro": 0, "Total Participación": 0, "Total Recibido": 0, "Partidas": 0}
            
            resumen_global[jugador["Rol"]]["Total Daño"] += jugador["Daño Infligido"]
            resumen_global[jugador["Rol"]]["Total Oro"] += jugador["Oro Total"]
            resumen_global[jugador["Rol"]]["Total Participación"] += jugador["Participación"]
            resumen_global[jugador["Rol"]]["Total Recibido"] += jugador["Daño Recibido"]
            resumen_global[jugador["Rol"]]["Partidas"] += 1

    # Mostrar el resumen global por rol
    for rol, datos in resumen_global.items():
        st.markdown(f"### {rol}")
        st.write(f"Total Daño: {datos['Total Daño']} mil")
        st.write(f"Total Oro: {datos['Total Oro']} mil")
        st.write(f"Total Participación: {datos['Total Participación']} %")
        st.write(f"Total Daño Recibido: {datos['Total Recibido']} mil")
        st.write(f"Promedio por Partida: {datos['Total Daño'] / datos['Partidas']:.2f} mil")
        st.write(f"Promedio Participación: {datos['Total Participación'] / datos['Partidas']:.2f} %")

        # Generar el gráfico de resumen
        fig_resumen = generar_grafico({
            "Daño Infligido": datos["Total Daño"] / datos["Partidas"],
            "Oro Total": datos["Total Oro"] / datos["Partidas"],
            "Participación": datos["Total Participación"] / datos["Partidas"],
            "Daño Recibido": datos["Total Recibido"] / datos["Partidas"]
        }, f"Resumen {rol}", maximos_globales)
        st.pyplot(fig_resumen)

    # Descargar imágenes con los gráficos
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        fecha_hoy = datetime.datetime.today().strftime('%Y-%m-%d')
        folder_path = f'./partidas/{fecha_hoy}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        for partida_num, partida_resultados in enumerate(partidas):
            for jugador in partida_resultados:
                fig = generar_grafico(jugador, jugador["Rol"], maximos_globales)
                fig_path = os.path.join(folder_path, f"partida_{partida_num + 1}_{jugador['Rol']}.png")
                fig.savefig(fig_path, dpi=300, bbox_inches='tight')
                zip_file.write(fig_path, os.path.basename(fig_path))

    zip_buffer.seek(0)
    st.download_button(
        label="📥 Descargar registro de todas las partidas",
        data=zip_buffer,
        file_name=f"Registro_Honor_of_Kings_{fecha_hoy}.zip",
        mime="application/zip"
    )
