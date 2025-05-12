import streamlit as st
import pandas as pd
import altair as alt
from fpdf import FPDF
from datetime import date

st.set_page_config(page_title="WOLF SEEKERS E-SPORTS - Tracker", layout="wide")
st.title("🐺 WOLF SEEKERS E-SPORTS - Registro Diario")

# Define roles y métricas
roles = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
metricas = ["Oro", "Daño Infligido", "Daño Recibido", "Participación", "Asesinatos", "Muertes", "Asistencias"]

# Inicializa sesión
if "datos" not in st.session_state:
    st.session_state.datos = {rol: [] for rol in roles}

# Tabs
tabs = st.tabs(["Registrar Partida", "Resumen Diario", "Exportar PDF"])

# REGISTRO DE PARTIDA
tab = tabs[0]
with tab:
    st.subheader("Registrar Rendimiento por Línea")
    for rol in roles:
        with st.expander(f"Registro - {rol}"):
            datos = {}
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                datos["Oro"] = st.number_input(f"{rol} - Oro", 0, 20000, 10000, key=f"{rol}_oro")
                datos["Daño Infligido"] = st.number_input(f"{rol} - Daño Infligido", 0, 100000, 50000, key=f"{rol}_dano_infl")
            with col2:
                datos["Daño Recibido"] = st.number_input(f"{rol} - Daño Recibido", 0, 100000, 30000, key=f"{rol}_dano_rec")
                datos["Participación"] = st.slider(f"{rol} - Participación en %", 0, 100, 50, key=f"{rol}_part")
            with col3:
                datos["Asesinatos"] = st.number_input(f"{rol} - Asesinatos", 0, 50, 5, key=f"{rol}_kills")
                datos["Muertes"] = st.number_input(f"{rol} - Muertes", 0, 50, 5, key=f"{rol}_deaths")
            with col4:
                datos["Asistencias"] = st.number_input(f"{rol} - Asistencias", 0, 50, 5, key=f"{rol}_assists")
            if st.button(f"Guardar {rol}", key=f"guardar_{rol}"):
                st.session_state.datos[rol].append(datos)
                st.success(f"Datos guardados para {rol}")

# RESUMEN Y ANÁLISIS
def analizar_rendimiento(medias):
    feedback = []
    if medias["Participación"] >= 70 and medias["Asesinatos"] >= 8:
        feedback.append("🔥 Excelente participación ofensiva.")
    elif medias["Participación"] >= 50:
        feedback.append("👍 Buena participación.")
    else:
        feedback.append("⚠️ Baja participación, busca más presencia en peleas.")

    if medias["Muertes"] > 10:
        feedback.append("❌ Demasiadas muertes, mejora posicionamiento.")
    if medias["Asistencias"] < 5:
        feedback.append("📉 Pocas asistencias, colabora más con el equipo.")

    return " \\n".join(feedback)


tab2 = tabs[1]
with tab2:
    st.subheader("📊 Resumen Diario por Línea")
    for rol in roles:
        datos_rol = st.session_state.datos[rol]
        if datos_rol:
            df = pd.DataFrame(datos_rol)
            medias = df.mean(numeric_only=True)
            st.markdown(f"### {rol}")
            st.dataframe(df, use_container_width=True)

            st.metric("Promedio Oro", f"{medias['Oro']:.0f}")
            st.metric("Promedio Daño Infligido", f"{medias['Daño Infligido']:.0f}")
            st.metric("Promedio Participación", f"{medias['Participación']:.1f}%")
            
            grafico = alt.Chart(df.reset_index()).transform_fold(
                ["Oro", "Daño Infligido", "Daño Recibido", "Participación"]
            ).mark_line(point=True).encode(
                x='index:O',
                y=alt.Y('value:Q', scale=alt.Scale(zero=False)),
                color='key:N',
                tooltip=['key', 'value']
            ).properties(height=300)

            st.altair_chart(grafico, use_container_width=True)
            st.info(analizar_rendimiento(medias))
        else:
            st.warning(f"Sin datos aún para {rol}.")

# EXPORTAR PDF
tab3 = tabs[2]
with tab3:
    st.subheader("📄 Exportar Datos a PDF")
    if st.button("Exportar todo como PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "WOLF SEEKERS E-SPORTS - Registro Diario", ln=True, align="C")
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Fecha: {date.today().isoformat()}", ln=True, align="C")

        for rol in roles:
            datos_rol = st.session_state.datos[rol]
            if datos_rol:
                df = pd.DataFrame(datos_rol)
                medias = df.mean(numeric_only=True)

                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, f"{rol}", ln=True)
                pdf.set_font("Arial", '', 10)
                for metrica in metricas:
                    promedio = medias[metrica]
                    pdf.cell(200, 8, f"{metrica}: {promedio:.2f}", ln=True)
                pdf.multi_cell(0, 10, f"Feedback: {analizar_rendimiento(medias)}")
                pdf.ln(4)

        pdf.output("registro_diario_wolfseekers.pdf")
        st.success("PDF generado exitosamente como 'registro_diario_wolfseekers.pdf'")
