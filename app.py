import streamlit as st
import pandas as pd
import altair as alt
import base64
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

# — Diccionario de usuarios y contraseñas —
USUARIOS = {"Tivi": "2107", "Ghost": "203"}

def login(username, password):
    if username in USUARIOS and USUARIOS[username] == password:
        return True, "Inicio de sesión exitoso!"
    return False, "Usuario o contraseña incorrectos"

st.set_page_config(page_title="WOLF SEEKERS - Tracker Diario", layout="wide")

# — Traducciones simples —
tr = {
    "registro": "📋 Registro",
    "historial": "📚 Historial",
    "promedio": "📈 Promedio",
    "grafico": "📊 Comparativa Visual",
    "feedback": "🗣️ Feedback",
    "jugador": "👤 Rendimiento por Línea",
    "guardar": "💾 Guardar partida",
    "exportar": "📤 Exportar a HTML",
    "rendimiento": "Rendimiento (%)",
    "kda": "📝 Registro KDA"
}

# — Sidebar de navegación —
st.sidebar.title("Menú")
seccion = st.sidebar.radio("", [
    tr["registro"],
    tr["kda"],
    tr["historial"],
    tr["promedio"],
    tr["feedback"],
    tr["jugador"]
])

# — Login sencillo corregido —
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🐺 WOLF SEEKERS E-SPORTS")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        ok, msg = login(user, pwd)
        st.session_state.logged_in = ok
        if ok:
            st.success(msg)
        else:
            st.error(msg)
    st.stop()

# — Estructuras de datos en session_state —
if "partidas" not in st.session_state:
    st.session_state.partidas = []
if "contador" not in st.session_state:
    st.session_state.contador = 1

# Acumulado KDA por línea (nuevo dict en session_state)
if "kda_acumulado" not in st.session_state:
    st.session_state.kda_acumulado = {linea: {"Asesinatos":0, "Muertes":0, "Asistencias":0} for linea in ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]}

lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]

problemas_comunes = [
    "Poco farmeo",
    "Mala visión / wards",
    "Mal posicionamiento",
    "Falta de roaming",
    "Objetivos ignorados",
    "Mal tradeo en línea",
    "No seguimiento de ganks",
    "Falta de comunicación",
    "Teamfights descoordinadas"
]

pesos = {
    "TOPLANER": {"oro":0.2, "dano":0.3, "part":0.2, "kda":0.3},
    "JUNGLA":   {"oro":0.2, "dano":0.25,"part":0.25,"kda":0.3},
    "MIDLANER": {"oro":0.2, "dano":0.3, "part":0.2, "kda":0.3},
    "ADC":      {"oro":0.2, "dano":0.2, "part":0.3, "kda":0.3},
    "SUPPORT":  {"oro":0.1, "dano":0.1, "part":0.4, "kda":0.4}
}

def calcular_puntaje(fila):
    rol = fila["Línea"]
    p = pesos[rol]
    kda = (fila.get("Asesinatos",0) + fila.get("Asistencias",0)) / max(1, fila.get("Muertes",0))
    val_oro = fila.get("Oro",0) / 15000
    val_dano = fila.get("Daño Infligido",0) / 100000
    val_part = fila.get("Participación (%)",0) / 100
    eficiencia = (
        val_oro * p["oro"] +
        val_dano * p["dano"] +
        val_part * p["part"] +
        (kda / 5) * p["kda"]
    )
    return round(eficiencia * 100, 2)

def sugerencias(fila):
    msgs = []
    if fila.get("Daño Infligido",0) < 20000:
        msgs.append("🔸 Aumenta tu farmeo y participa en peleas tempranas.")
    if fila.get("Participación (%)",0) < 50:
        msgs.append("🔸 Sé más activo en objetivos de equipo.")
    if (fila.get("Asesinatos",0) + fila.get("Asistencias",0)) / max(1, fila.get("Muertes",0)) < 1:
        msgs.append("🔸 Mejora tu posicionamiento para no morir tanto.")
    return "\n".join(msgs) or "✅ Buen equilibrio de métricas."

def exportar_html(df_partidas, df_promedios, df_feedback):
    html = f"""
    <html><head><title>Reporte WOLF SEEKERS</title></head><body>
    <h1>Reporte de partidas</h1>
    {df_partidas.to_html(index=False)}

    <h2>Promedios de rendimiento por línea</h2>
    {df_promedios.to_html(index=False)}

    <h2>Feedback por línea</h2>
    {df_feedback.to_html(index=False)}

    <h2>Gráficos de rendimiento por línea</h2>
    """

    # Agregar gráficos para cada línea
    for linea in lineas:
        fig, ax = plt.subplots(figsize=(7,4))
        df_linea = df_partidas[df_partidas["Línea"]==linea]
        if df_linea.empty:
            continue
        ax.plot(df_linea["Partida"], df_linea["Rendimiento"], marker='o')
        ax.set_title(f"Rendimiento a lo largo de las partidas - {linea}")
        ax.set_xlabel("Partida")
        ax.set_ylabel("Rendimiento (%)")
        ax.grid(True)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        img_tag = f'<h3>{linea}</h3><img src="data:image/png;base64,{data}" alt="Gráfico Rendimiento {linea}" />'
        html += img_tag

    html += "</body></html>"
    return html

def descargar_html(html, nombre_archivo="reporte_wolf_seekers.html"):
    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{nombre_archivo}">📥 Descargar reporte HTML</a>'
    st.markdown(href, unsafe_allow_html=True)

# — Sección REGISTRO SIN KDA —
if seccion == tr["registro"]:
    st.header(tr["registro"])
    datos = []
    for linea in lineas:
        with st.expander(linea):
            dano = st.number_input("Daño Infligido", 0, step=100, key=f"dano_{linea}")
            rec = st.number_input("Daño Recibido", 0, step=100, key=f"dr_{linea}")
            oro = st.number_input("Oro", 0, step=100, key=f"oro_{linea}")
            part = st.slider("Participación %", 0, 100, key=f"part_{linea}")

            seleccion = st.multiselect(
                "Problemas detectados",
                problemas_comunes,
                key=f"pc_{linea}"
            )
            otro = st.text_input("Otro problema (escribe aquí)", key=f"otro_{linea}")
            comentarios = seleccion.copy()
            if otro:
                comentarios.append(f"Otro: {otro}")

            datos.append({
                "Línea": linea, "Oro": oro, "Daño Infligido": dano,
                "Daño Recibido": rec, "Participación (%)": part,
                "Comentarios": "; ".join(comentarios),
                # Inicializamos KDA en 0 para evitar problemas al calcular puntaje
                "Asesinatos": 0,
                "Muertes": 0,
                "Asistencias": 0
            })
    if st.button(tr["guardar"]):
        df = pd.DataFrame(datos)
        partida_id = st.session_state.contador
        df["Partida"] = f"Partida {partida_id}"
        df["Rendimiento"] = df.apply(calcular_puntaje, axis=1)
        st.session_state.partidas.append(df)
        st.session_state.contador += 1
        st.success(f"Partida {partida_id} guardada correctamente.")

# — Sección KDA (acumulado) —
elif seccion == tr["kda"]:
    st.header(tr["kda"])
    st.write("Aquí se registran las estadísticas KDA por línea acumuladas del día.")

    with st.form("form_kda"):
        linea_sel = st.selectbox("Selecciona la línea", lineas, key="linea_kda")
        ases = st.number_input("Asesinatos", min_value=0, step=1, key="ases_kda")
        muer = st.number_input("Muertes", min_value=0, step=1, key="muer_kda")
        asis = st.number_input("Asistencias", min_value=0, step=1, key="asis_kda")
        enviar = st.form_submit_button("Agregar KDA")

        if enviar:
            kda_act = st.session_state.kda_acumulado[linea_sel]
            kda_act["Asesinatos"] += ases
            kda_act["Muertes"] += muer
            kda_act["Asistencias"] += asis
            st.success(f"KDA acumulado actualizado para {linea_sel}.")

    # Mostrar tabla con KDA acumulado por línea
    df_kda = pd.DataFrame([
        {"Línea": lin,
         "Asesinatos": vals["Asesinatos"],
         "Muertes": vals["Muertes"],
         "Asistencias": vals["Asistencias"],
         "KDA": round((vals["Asesinatos"] + vals["Asistencias"]) / max(1, vals["Muertes"]), 2)
        } for lin, vals in st.session_state.kda_acumulado.items()
    ])
    st.dataframe(df_kda)

# — Sección HISTORIAL —
elif seccion == tr["historial"]:
    st.header(tr["historial"])
    if not st.session_state.partidas:
        st.info("No se han registrado partidas aún.")
    else:
        df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
        st.dataframe(df_hist)

# — Sección PROMEDIO —
elif seccion == tr["promedio"]:
    st.header(tr["promedio"])
    if not st.session_state.partidas:
        st.info("No hay datos para mostrar promedios.")
    else:
        df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
        promedios = df_hist.groupby("Línea").agg({
            "Rendimiento": "mean",
            "Oro": "mean",
            "Daño Infligido": "mean",
            "Daño Recibido": "mean",
            "Participación (%)": "mean"
        }).reset_index()
        promedios["Rendimiento"] = promedios["Rendimiento"].round(2)
        st.dataframe(promedios)

# — Sección FEEDBACK —
elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    if not st.session_state.partidas:
        st.info("No hay datos para generar feedback.")
    else:
        df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
        df_hist["Sugerencias"] = df_hist.apply(sugerencias, axis=1)
        st.dataframe(df_hist[["Línea", "Partida", "Rendimiento", "Sugerencias"]])

# — Sección RENDIMIENTO POR LÍNEA (jugador) —
elif seccion == tr["jugador"]:
    st.header(tr["jugador"])
    if not st.session_state.partidas:
        st.info("No hay datos para mostrar gráficos.")
    else:
        df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
        linea_sel = st.selectbox("Selecciona la línea", lineas)
        df_linea = df_hist[df_hist["Línea"]==linea_sel]

        if df_linea.empty:
            st.warning("No hay partidas registradas para esta línea.")
        else:
            chart = (
                alt.Chart(df_linea)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Partida:N", title="Partida"),
                    y=alt.Y("Rendimiento:Q", title="Rendimiento (%)"),
                    tooltip=["Partida", "Rendimiento"]
                )
                .properties(title=f"Rendimiento de {linea_sel} por partida")
            )
            st.altair_chart(chart, use_container_width=True)

# — Exportar datos a HTML —
if st.session_state.partidas:
    df_partidas = pd.concat(st.session_state.partidas, ignore_index=True)
    df_promedios = df_partidas.groupby("Línea").agg({"Rendimiento":"mean"}).reset_index()
    df_promedios["Rendimiento"] = df_promedios["Rendimiento"].round(2)
    df_feedback = df_partidas.copy()
    df_feedback["Sugerencias"] = df_feedback.apply(sugerencias, axis=1)
    html = exportar_html(df_partidas, df_promedios, df_feedback)
    descargar_html(html)
