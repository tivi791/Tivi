import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="WOLF SEEKERS - Tracker Diario", layout="wide")

st.title("🐺 WOLF SEEKERS E-SPORTS - Registro Diario de Rendimiento por Línea")

lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
datos = []

st.subheader("📋 Registro de Rendimiento")

for linea in lineas:
    with st.expander(f"Registro - {linea}", expanded=True):
        oro = st.number_input(f"{linea} - Oro", min_value=0, step=100, key=f"oro_{linea}")
        dano_infligido = st.number_input(f"{linea} - Daño Infligido", min_value=0, step=100, key=f"di_{linea}")
        dano_recibido = st.number_input(f"{linea} - Daño Recibido", min_value=0, step=100, key=f"dr_{linea}")
        participacion = st.slider(f"{linea} - Participación en %", 0, 100, key=f"p_{linea}")
        asesinatos = st.number_input(f"{linea} - Asesinatos", min_value=0, step=1, key=f"a_{linea}")
        muertes = st.number_input(f"{linea} - Muertes", min_value=0, step=1, key=f"m_{linea}")
        asistencias = st.number_input(f"{linea} - Asistencias", min_value=0, step=1, key=f"as_{linea}")

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

# Calcular rendimiento por línea
def calcular_puntaje(fila):
    kda = (fila["Asesinatos"] + fila["Asistencias"]) / max(1, fila["Muertes"])
    eficiencia = (
        (fila["Oro"] / 15000) * 0.2 +
        (fila["Daño Infligido"] / 100000) * 0.2 +
        (fila["Participación (%)"] / 100) * 0.2 +
        (kda / 5) * 0.4
    )
    return round(eficiencia * 100, 2)

df["Rendimiento (%)"] = df.apply(calcular_puntaje, axis=1)

st.subheader("📊 Análisis de Rendimiento")
st.dataframe(df, use_container_width=True)

# Retroalimentación
def feedback(puntaje):
    if puntaje >= 85:
        return "🔥 Excelente desempeño. Sigue así."
    elif puntaje >= 70:
        return "✅ Buen desempeño. Puedes pulir algunos detalles."
    elif puntaje >= 50:
        return "⚠️ Rendimiento regular. Necesita ajustes."
    else:
        return "❌ Bajo rendimiento. Revisar toma de decisiones."

df["Feedback"] = df["Rendimiento (%)"].apply(feedback)

# Mostrar retroalimentación
st.subheader("🗣️ Retroalimentación por Línea")
for index, row in df.iterrows():
    st.markdown(f"**{row['Línea']}** → {row['Feedback']} ({row['Rendimiento (%)']}%)")

# Gráfico
st.subheader("📈 Comparativa Visual")

try:
    grafico = alt.Chart(df).mark_bar().encode(
        x=alt.X("Línea:N", title="Rol"),
        y=alt.Y("Rendimiento (%):Q", title="Puntaje de Rendimiento"),
        color="Línea:N",
        tooltip=["Línea", "Rendimiento (%)"]
    ).properties(
        width=600,
        height=400,
        title="Desempeño por Línea"
    )

    st.altair_chart(grafico, use_container_width=True)
except Exception as e:
    st.error(f"Ocurrió un error al generar el gráfico: {e}")
