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
        st.success(f"Partida {partida_id} guardada correctamente")

# — Pestaña KDA —
elif seccion == tr["kda"]:
    st.header(tr["kda"])
    if not st.session_state.partidas:
        st.info("Primero debes registrar al menos una partida en la pestaña Registro")
        st.stop()

    partidas_existentes = [f"Partida {i+1}" for i in range(len(st.session_state.partidas))]
    sel_partida = st.selectbox("Selecciona partida para ingresar KDA", partidas_existentes)

    ases = st.number_input("Asesinatos", 0, 20, step=1)
    muer = st.number_input("Muertes", 0, 20, step=1)
    asist = st.number_input("Asistencias", 0, 20, step=1)

    if st.button("Guardar KDA"):
        idx = int(sel_partida.split()[-1]) - 1
        df = st.session_state.partidas[idx]
        df["Asesinatos"] = ases
        df["Muertes"] = muer
        df["Asistencias"] = asist
        df["Rendimiento"] = df.apply(calcular_puntaje, axis=1)
        st.session_state.partidas[idx] = df
        st.success("KDA actualizado y rendimiento recalculado")

# — HISTORIAL DE PARTIDAS —
elif seccion == tr["historial"]:
    st.header(tr["historial"])
    if not st.session_state.partidas:
        st.info("No hay partidas registradas aún.")
        st.stop()

    df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
    st.dataframe(df_hist)

# — PROMEDIOS POR LÍNEA —
elif seccion == tr["promedio"]:
    st.header(tr["promedio"])
    if not st.session_state.partidas:
        st.info("No hay partidas registradas aún.")
        st.stop()

    df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
    df_prom = df_hist.groupby("Línea").agg({
        "Oro": "mean",
        "Daño Infligido": "mean",
        "Daño Recibido": "mean",
        "Participación (%)": "mean",
        "Rendimiento": "mean"
    }).reset_index()
    df_prom["Rendimiento"] = df_prom["Rendimiento"].round(2)
    st.dataframe(df_prom)

# — FEEDBACK GENERAL POR LÍNEA —
elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    if not st.session_state.partidas:
        st.info("No hay partidas registradas aún.")
        st.stop()
    df_hist = pd.concat(st.session_state.partidas, ignore_index=True)

    data_feedback = []
    for linea in lineas:
        df_l = df_hist[df_hist["Línea"] == linea]
        if df_l.empty:
            continue
        promedio_rend = df_l["Rendimiento"].mean()
        suger = sugerencias(df_l.iloc[-1])
        data_feedback.append({
            "Línea": linea,
            "Rendimiento promedio": round(promedio_rend, 2),
            "Sugerencias": suger
        })
    df_feedback = pd.DataFrame(data_feedback)
    st.dataframe(df_feedback)

# — RENDIMIENTO POR LÍNEA CON GRÁFICOS —
elif seccion == tr["jugador"]:
    st.header(tr["jugador"])
    if not st.session_state.partidas:
        st.info("No hay partidas registradas aún.")
        st.stop()

    df_hist = pd.concat(st.session_state.partidas, ignore_index=True)
    st.selectbox("Selecciona línea para ver rendimiento", lineas, key="linea_graf")

    linea_sel = st.session_state.linea_graf
    df_linea = df_hist[df_hist["Línea"] == linea_sel].copy()
    if df_linea.empty:
        st.warning(f"No hay datos para {linea_sel}")
    else:
        # Gráfico Altair
        chart = alt.Chart(df_linea).mark_line(point=True).encode(
            x="Partida",
            y="Rendimiento",
            tooltip=["Partida", "Rendimiento"]
        ).properties(width=700, height=400, title=f"Rendimiento en {linea_sel} por partida")
        st.altair_chart(chart, use_container_width=True)

# — EXPORTAR A HTML EN EL SIDEBAR —
if seccion != tr["registro"]:
    if st.sidebar.button(tr["exportar"]):
        if not st.session_state.partidas:
            st.sidebar.warning("No hay datos para exportar.")
        else:
            df_partidas = pd.concat(st.session_state.partidas, ignore_index=True)
            df_promedios = df_partidas.groupby("Línea").agg({
                "Oro": "mean",
                "Daño Infligido": "mean",
                "Daño Recibido": "mean",
                "Participación (%)": "mean",
                "Rendimiento": "mean"
            }).reset_index()
            df_promedios["Rendimiento"] = df_promedios["Rendimiento"].round(2)

            data_feedback = []
            for linea in lineas:
                df_l = df_partidas[df_partidas["Línea"] == linea]
                if df_l.empty:
                    continue
                promedio_rend = df_l["Rendimiento"].mean()
                suger = sugerencias(df_l.iloc[-1])
                data_feedback.append({
                    "Línea": linea,
                    "Rendimiento promedio": round(promedio_rend, 2),
                    "Sugerencias": suger
                })
            df_feedback = pd.DataFrame(data_feedback)

            html = exportar_html(df_partidas, df_promedios, df_feedback)
            descargar_html(html)
