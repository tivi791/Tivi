import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="WOLF SEEKERS - Tracker Diario", layout="wide")

# Idioma
idioma = st.selectbox("🌐 Elige idioma / Select language", ["Español", "English"])

# Traducciones
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
        "puntaje": "Puntaje de Rendimiento"
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
        "puntaje": "Performance Score"
    }
}

# Traducción activa
tr = T[idioma]

st.title(tr["titulo"])

lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
datos = []

st.subheader(tr["registro"])

for linea in lineas:
    with st.expander(f"{linea}", expanded=True):
        oro = st.number_input(f"{linea} - {tr['oro']}", min_value=0, step=100, key=f"oro_{linea}")
        dano_infligido = st.number_input(f"{linea} - {tr['dano_i']}", min_value=0, step=100, key=f"di_{linea}")
        dano_recibido = st.number_input(f"{linea} - {tr['dano_r']}", min_value=0, step=100, key=f"dr_{linea}")
        participacion = st.slider(f"{linea} - {tr['participacion']}", 0, 100, key=f"p_{linea}")
        asesinatos = st.number_input(f"{linea} - {tr['asesinatos']}", min_value=0, step=1, key=f"a_{linea}")
        muertes = st.number_input(f"{linea} - {tr['muertes']}", min_value=0, step=1, key=f"m_{linea}")
        asistencias = st.number_input(f"{linea} - {tr['asistencias']}", min_value=0, step=1, key=f"as_{linea}")

        datos.append({
            "Línea": linea,
            "Oro": oro,
            "Daño Infligido": dano_infligido,
            "Daño Recibido": dano_recibido,
            "Participación (%)": participacion,
            "Asesinatos": asesinatos,
            "Muertes": muertes,
            "Asistencias": asistencias
        })

df = pd.DataFrame(datos)

# Cálculo de rendimiento
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

# Feedback
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

# Estado de sesión para guardar partidas
if "partidas_dia" not in st.session_state:
    st.session_state.partidas_dia = []

# Botón para guardar
if st.button(tr["guardar"]):
    st.session_state.partidas_dia.append(df.copy())
    st.success(tr["guardado"])

# Mostrar historial
if st.session_state.partidas_dia:
    st.subheader(tr["historial"])
    partidas_df = pd.concat(
        st.session_state.partidas_dia,
        keys=range(1, len(st.session_state.partidas_dia)+1),
        names=["Partida", "Índice"]
    ).reset_index()
    st.dataframe(partidas_df, use_container_width=True)

    # Promedio por línea
    promedio = partidas_df.groupby("Línea").mean(numeric_only=True).reset_index()
    st.subheader(tr["promedio"])
    st.dataframe(promedio)

    # Gráfico
    st.subheader(tr["grafico"])
    try:
        chart = alt.Chart(promedio).mark_bar().encode(
            x=alt.X("Línea:N", title=tr["rol"]),
            y=alt.Y(f"{tr['rendimiento']}:Q", title=tr["puntaje"]),
            color="Línea:N",
            tooltip=["Línea", tr["rendimiento"]]
        ).properties(
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Ocurrió un error al generar el gráfico: {e}")

    # Feedback visual
    st.subheader(tr["feedback"])
    for index, row in promedio.iterrows():
        st.markdown(f"**{row['Línea']}** → {feedback(row[tr['rendimiento']])} ({row[tr['rendimiento']]}%)")
