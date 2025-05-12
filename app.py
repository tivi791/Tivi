import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import base64
import os
from datetime import datetime

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

# Títulos y etiquetas en español
tr = {
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
    "exportar": "📤 Exportar todo a HTML"
}

st.title(tr["titulo"])
username = st.text_input("Nombre de usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    success, message = login(username, password)
    st.session_state.logged_in = success
    if success:
        st.success(message)
    else:
        st.error(message)

if st.session_state.get("logged_in", False):
    lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
    
    # Inicializar estado
    if "partidas_dia" not in st.session_state:
        st.session_state.partidas_dia = []
    if "partida_count" not in st.session_state:
        st.session_state.partida_count = 1

    tab1, tab2, tab3, tab4 = st.tabs([
        tr["registro"], 
        tr["historial"], 
        tr["promedio"], 
        tr["feedback"]
    ])

    # Pestaña 1: Registro
    with tab1:
        st.markdown("### 📌 Ingresa los datos por línea:")
        datos = []
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

        def feedback_text(puntaje):
            if puntaje >= 85:
                return "🔥 Excelente desempeño. Sigue así."
            elif puntaje >= 70:
                return "✅ Buen desempeño. Puedes pulir algunos detalles."
            elif puntaje >= 50:
                return "⚠️ Rendimiento regular. Necesita ajustes."
            else:
                return "❌ Bajo rendimiento. Revisar toma de decisiones."

        df["Feedback"] = df[tr["rendimiento"]].apply(feedback_text)

        if st.button(tr["guardar"]):
            partida_id = f"Partida {st.session_state.partida_count}"
            df["Partida"] = partida_id
            st.session_state.partidas_dia.append(df.copy())
            st.session_state.partida_count += 1
            st.success(tr["guardado"])

    # Pestaña 2: Historial
    with tab2:
        st.header(tr["historial"])
        if st.session_state.partidas_dia:
            historial_df = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            st.dataframe(historial_df)
        else:
            st.info("No hay partidas guardadas.")

    # Pestaña 3: Promedio y Gráfico
    with tab3:
        st.header(tr["promedio"])
        if st.session_state.partidas_dia:
            df_all = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            promedio = df_all.groupby("Línea").mean(numeric_only=True).reset_index()
            st.dataframe(promedio)

            # Gráfico Altair
            melted = promedio.melt(
                id_vars=["Línea"],
                value_vars=["Oro", "Daño Infligido", "Daño Recibido", "Participación (%)", tr["rendimiento"]]
            )
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X("Línea:N", title="Línea"),
                y=alt.Y("value:Q", title="Valor Promedio"),
                color="variable:N",
                tooltip=["Línea", "variable", "value"]
            ).properties(width=700)
            st.altair_chart(chart, use_container_width=True)

            # Guardar gráfico Matplotlib y codificar en base64
            fig, ax = plt.subplots(figsize=(10, 5))
            for var in ["Oro", "Daño Infligido", "Daño Recibido", "Participación (%)", tr["rendimiento"]]:
                ax.plot(promedio["Línea"], promedio[var], marker='o', label=var)
            ax.set_title("Promedio de Rendimiento por Línea")
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            grafico_path = "grafico_promedio.png"
            fig.savefig(grafico_path)
            with open(grafico_path, "rb") as img_file:
                encoded_img = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            st.info("No hay partidas para calcular el promedio.")

    # Pestaña 4: Feedback con barra de progreso
    with tab4:
        st.header(tr["feedback"])
        if st.session_state.partidas_dia:
            feedback_df = pd.concat(st.session_state.partidas_dia, ignore_index=True)
            for linea in lineas:
                sub = feedback_df[feedback_df["Línea"] == linea]
                avg = sub[tr["rendimiento"]].mean()
                progreso = int(round(avg))
                progreso = max(0, min(progreso, 100))
                st.subheader(linea)
                st.progress(progreso)
                st.write(f"**Rendimiento Promedio:** {round(avg, 2)}%")
        else:
            st.info("No hay partidas para mostrar retroalimentación.")

    # Exportar a HTML
    if st.button(tr["exportar"]):
        if st.session_state.partidas_dia and 'promedio' in locals() and grafico_path:
            html_content = f"""
            <html>
            <head><title>Reporte Diario de Rendimiento</title></head>
            <body>
                <h1 style="text-align: center;">{tr['titulo']}</h1>
                <h2>{tr['promedio']}</h2>
                {promedio.to_html(index=False)}
                <h3>{tr['grafico']}</h3>
                <img src="data:image/png;base64,{encoded_img}" alt="Gráfico Promedio" width="800">
            </body>
            </html>
            """
            html_path = "registro_diario.html"
            with open(html_path, "w") as file:
                file.write(html_content)
            with open(html_path, "r") as f:
                st.download_button(
                    label="Descargar Reporte Diario",
                    data=f,
                    file_name=html_path,
                    mime="text/html"
                )
        else:
            st.warning("No hay datos para exportar.")
