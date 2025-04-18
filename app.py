import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# Función para descargar gráficos como imagen
def get_img_download_link(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="grafico.png">Descargar gráfico</a>'
    return href

# Función para generar gráficos radiales
def generar_grafico(daño, daño_recibido, oro, participacion, rol):
    labels = ['Daño Infligido', 'Daño Recibido', 'Oro Total', 'Participación']
    values = [daño, daño_recibido, oro, participacion]

    # Normalización de valores
    max_value = max(values)
    normalized_values = [v / max_value * 100 for v in values]

    # Gráfico radial
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]  # Cerrar el gráfico
    angles += angles[:1]

    ax.fill(angles, normalized_values + [normalized_values[0]], color='green', alpha=0.25)
    ax.plot(angles, normalized_values + [normalized_values[0]], color='green', linewidth=2)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=13, weight='bold')

    ax.set_title(f'{rol} - Gráfico Radial', color='white', fontsize=16, weight='bold', pad=20)
    ax.grid(color='gray', linestyle='--', alpha=0.3)

    return fig

# Función para generar retroalimentación
def generar_feedback(daño, daño_recibido, oro, participacion, rol):
    feedback = ""
    
    if daño > 100000:
        feedback += f"{rol}: Gran desempeño en daño infligido. Mantén la presión.\n"
    elif daño < 50000:
        feedback += f"{rol}: El daño infligido fue bajo. Necesitas mejorar en las peleas.\n"
    
    if daño_recibido > 100000:
        feedback += f"{rol}: Has recibido mucho daño. Ten cuidado en las peleas.\n"
    
    if oro > 15000:
        feedback += f"{rol}: Excelente farmeo. Sigue con ese ritmo.\n"
    elif oro < 8000:
        feedback += f"{rol}: Necesitas farmear más para mantenerte competitivo.\n"
    
    if participacion > 30:
        feedback += f"{rol}: Gran participación en las peleas. Sigue así.\n"
    elif participacion < 10:
        feedback += f"{rol}: Baja participación en el juego. Intenta involucrarte más en las peleas.\n"
    
    return feedback

# Interfaz de Streamlit
st.title("Honor of Kings - Análisis Profesional por Rol")

st.image("logo_equipo.png", width=120)  # Imagen del equipo (opcional)

# Recoger datos para cada rol
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]
datos = {}

for rol in roles:
    with st.expander(f"📝 Ingresar datos para {rol}"):
        daño = st.number_input(f"Daño Infligido {rol} (mil)", min_value=0, step=1000)
        daño_recibido = st.number_input(f"Daño Recibido {rol} (mil)", min_value=0, step=1000)
        oro = st.number_input(f"Oro Total {rol} (mil)", min_value=0, step=1000)
        participacion = st.slider(f"Participación {rol} (%)", 0, 100, 0)
        datos[rol] = (daño, daño_recibido, oro, participacion)

# Crear los gráficos y retroalimentación
col1, col2 = st.columns(2)
for rol, (daño, daño_recibido, oro, participacion) in datos.items():
    with col1:
        # Generar gráfico
        fig = generar_grafico(daño, daño_recibido, oro, participacion, rol)
        st.pyplot(fig)
    with col2:
        # Generar retroalimentación
        feedback = generar_feedback(daño, daño_recibido, oro, participacion, rol)
        st.markdown(f"### Análisis de {rol}")
        st.markdown(feedback)

# Botón para descargar los gráficos
st.markdown("### Descargar todos los gráficos")
for rol, (daño, daño_recibido, oro, participacion) in datos.items():
    fig = generar_grafico(daño, daño_recibido, oro, participacion, rol)
    download_link = get_img_download_link(fig)
    st.markdown(download_link, unsafe_allow_html=True)

