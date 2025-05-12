import streamlit as st
import pandas as pd
import altair as alt
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

# Diccionario de usuarios y contraseñas
USUARIOS = {"Tivi": "2107", "Ghost": "203"}

# Función para iniciar sesión
def login(username, password):
    if username in USUARIOS:
        if USUARIOS[username] == password:
            return True, "Inicio de sesión exitoso!"
        else:
            return False, "Contraseña incorrecta"
    else:
        return False, "Usuario no encontrado"

# Configuración de la página
st.set_page_config(page_title="WOLF SEEKERS - Tracker Diario", layout="wide")

idioma = st.selectbox("🌐 Elige idioma / Select language", ["Español", "English"])

T = {
    "Español": {
        "titulo": "🐺 WOLF SEEKERS E-SPORTS - Registro Diario de Rendimiento por Línea",
        "registro": "📋 Registro de Rendimiento",
        "guardar": "💾 Guardar esta partida",
        "guardado": "✅ Partida guardada correctamente.",
        "historial": "📚 Historial de partidas del día",
        "promedio": "📈 Promedio de rendimiento por línea",
        "grafico": "📊 Comparativa Visual",
        "feedback": "🗣️ Retroalimentación por Línea",
        "oro": "Oro",
        "dano_i": "Daño Infligido",
        "dano_r": "Daño Recibido",
        "participacion": "Participación en %",
        "asesinatos": "Asesinatos",
        "muertes": "Muertes",
        "asistencias": "Asistencias",
        "rendimiento": "Rendimiento (%)",
        "excelente": "🔥 Excelente desempeño. Sigue así.",
        "bueno": "✅ Buen desempeño. Puedes pulir algunos detalles.",
        "regular": "⚠️ Rendimiento regular. Necesita ajustes.",
        "malo": "❌ Bajo rendimiento. Revisar toma de decisiones.",
        "rol": "Rol",
        "puntaje": "Puntaje de Rendimiento",
        "exportar": "📤 Exportar todo a PDF"
    },
    "English": {
        "titulo": "🐺 WOLF SEEKERS E-SPORTS - Daily Performance Tracker by Role",
        "registro": "📋 Performance Entry",
        "guardar": "💾 Save this match",
        "guardado": "✅ Match saved successfully.",
        "historial": "📚 Match history of the day",
        "promedio": "📈 Average performance by role",
        "grafico": "📊 Visual Comparison",
        "feedback": "🗣️ Feedback by Role",
        "oro": "Gold",
        "dano_i": "Damage Dealt",
        "dano_r": "Damage Taken",
        "participacion": "Team Participation (%)",
        "asesinatos": "Kills",
        "muertes": "Deaths",
        "asistencias": "Assists",
        "rendimiento": "Performance (%)",
        "excelente": "🔥 Excellent performance. Keep it up!",
        "bueno": "✅ Good performance. Some details to improve.",
        "regular": "⚠️ Average performance. Needs adjustments.",
        "malo": "❌ Poor performance. Review your decisions.",
        "rol": "Role",
        "puntaje": "Performance Score",
        "exportar": "📤 Export all to PDF"
    }
}

tr = T[idioma]

# Login
st.title(tr["titulo"])
username = st.text_input("Nombre de usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    success, message = login(username, password)
    if success:
        st.session_state.logged_in = True
        st.success(message)
    else:
        st.session_state.logged_in = False
        st.error(f"Error: {message}")

if st.session_state.get("logged_in", False):
    lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
    datos = []

    tab1, tab2, tab3, tab4 = st.tabs([tr["registro"], tr["historial"], tr["promedio"], tr["feedback"]])

    with tab1:
        st.markdown("### 📌 Ingresa los datos por línea:")
        for linea in lineas:
            with st.expander(f"📍 {linea}", expanded=False):
                oro = st.number_input(f"{linea} - {tr['oro']}", 0, step=100, key=f"oro_{linea}")
                dano_i = st.number_input(f"{linea} - {tr['dano_i']}", 0, step=100, key=f"di_{linea}")
                dano_r = st.number_input(f"{linea} - {tr['dano_r']}", 0, step=100, key=f"dr_{linea}")
                participacion = st.slider(f"{linea} - {tr['participacion']}", 0, 100, key=f"p_{linea}")
                asesinatos = st.number_input(f"{linea} - {tr['asesinatos']}", 0, step=1, key=f"a_{linea}")
                muertes = st.number_input(f"{linea} - {tr['muertes']}", 0, step=1, key=f"m_{linea}")
                asistencias = st.number_input(f"{linea} - {tr['asistencias']}", 0, step=1, key=f"as_{linea}")

                datos.append({
                    "Línea": linea,
                    "Oro": oro,
                    "Daño Infligido": dano_i,
                    "Daño Recibido": dano_r,
                    "Participación (%)": participacion,
                    "Asesinatos": asesinatos,
                    "Muertes": muertes,
                    "Asistencias": asistencias
                })

        df = pd.DataFrame(datos)

        def calcular_puntaje(fila):
            kda = (fila["Asesinatos"] + fila["Asistencias"]) / max(1, fila["Muertes"])
            eficiencia = (
                (fila["Oro"] / 15000) * 0.2 +
                (fila["Daño Infligido"] / 100000) * 0.2 +
                (fila["Participación (%)"] / 100) * 0.2 +
                (kda / 5) * 0.4
            )
            return round(eficiencia * 100, 2)

        df[tr["rendimiento"]] = df.apply(calcular_puntaje, axis=1)

        def feedback(puntaje):
            if puntaje >= 85:
                return tr["excelente"]
            elif puntaje >= 70:
                return tr["bueno"]
            elif puntaje >= 50:
                return tr["regular"]
            else:
                return tr["malo"]

        df["Feedback"] = df[tr["rendimiento"]].apply(feedback)

        if "partidas_dia" not in st.session_state:
            st.session_state.partidas_dia = []

        if st.button(tr["guardar"]):
            st.session_state.partidas_dia.append(df.copy())
            st.success(tr["guardado"])

    with tab2:
        if st.session_state.partidas_dia:
            historial_df = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            st.write(historial_df)
        else:
            historial_df = pd.DataFrame()
            st.write("No hay partidas guardadas.")

    with tab3:
        if st.session_state.partidas_dia:
            df_completo = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            promedio = df_completo.groupby("Línea").mean(numeric_only=True).reset_index()
            st.dataframe(promedio)

            st.subheader(tr["grafico"])
            melted = promedio.melt(id_vars=["Línea"], value_vars=["Oro", "Daño Infligido", "Daño Recibido", "Participación (%)", tr["rendimiento"]])
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X("Línea:N", title=tr["rol"]),
                y=alt.Y("value:Q", title="Valor Promedio"),
                color="variable:N",
                tooltip=["Línea", "variable", "value"]
            ).properties(width=700)
            st.altair_chart(chart, use_container_width=True)

            # Guardar gráfico
            fig, ax = plt.subplots(figsize=(10, 5))
            for var in ["Oro", "Daño Infligido", "Daño Recibido", "Participación (%)", tr["rendimiento"]]:
                ax.plot(promedio["Línea"], promedio[var], marker='o', label=var)
            ax.set_title("Promedio de Rendimiento por Línea")
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            grafico_path = "grafico_promedio.png"
            plt.savefig(grafico_path)
        else:
            promedio = pd.DataFrame()
            grafico_path = None
            st.write("No hay partidas para calcular el promedio.")

    with tab4:
        if st.session_state.partidas_dia:
            feedback_df = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            feedback_df["Feedback"] = feedback_df[tr["rendimiento"]].apply(feedback)
            st.write(feedback_df)
        else:
            st.write("No hay partidas para mostrar retroalimentación.")

    # Exportar a PDF
    if st.button(tr["exportar"]):
        if not promedio.empty and grafico_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte Diario de Rendimiento", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt="Promedio de rendimiento por línea", ln=True)

            # Exportar tabla promedio
            for index, row in promedio.iterrows():
                pdf.cell(40, 10, row["Línea"], border=1)
                pdf.cell(40, 10, str(row["Oro"]), border=1)
                pdf.cell(40, 10, str(row["Daño Infligido"]), border=1)
                pdf.cell(40, 10, str(row["Daño Recibido"]), border=1)
                pdf.cell(40, 10, str(row["Participación (%)"]), border=1)
                pdf.cell(40, 10, str(row[tr["rendimiento"]]), border=1)
                pdf.ln()

            # Agregar gráficos al PDF
            if grafico_path:
                pdf.image(grafico_path, x=10, y=30, w=190)
                pdf.ln(100)

            # Generar PDF sin codificación adicional
            pdf.output("registro_diario.pdf")

            # Descargar el PDF
            st.download_button(label=tr["exportar"], data=open("registro_diario.pdf", "rb"), file_name="registro_diario.pdf", mime="application/pdf")
        else:
            st.warning("No hay suficientes datos para generar el PDF.")
