import streamlit as st
import pandas as pd
import altair as alt
import base64
from datetime import datetime

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
if "kda_partidas" not in st.session_state:
    st.session_state.kda_partidas = []

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

# — Sección REGISTRO SIN KDA (CAMBIO: ya no incluye Asesinatos, Muertes ni Asistencias) —
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
                "Comentarios": "; ".join(comentarios)
            })
    if st.button(tr["guardar"]):
        df = pd.DataFrame(datos)
        partida_id = st.session_state.contador
        df["Partida"] = f"Partida {partida_id}"
        df["Rendimiento"] = df.apply(calcular_puntaje, axis=1)
        st.session_state.partidas.append(df)
        st.session_state.contador += 1
        st.success(f"Partida {partida_id} guardada correctamente")

# — Nueva pestaña para registrar solo KDA —  
elif seccion == tr["kda"]:
    st.header(tr["kda"])
    if not st.session_state.partidas:
        st.info("Primero debes registrar al menos una partida en la pestaña Registro")
        st.stop()

    partidas_existentes = [f"Partida {i}" for i in range(1, st.session_state.contador)]
    partida_sel = st.selectbox("Selecciona la Partida", partidas_existentes)

    datos_kda = []
    for linea in lineas:
        with st.expander(linea):
            a = st.number_input("Asesinatos", 0, step=1, key=f"a_kda_{linea}")
            m = st.number_input("Muertes", 0, step=1, key=f"m_kda_{linea}")
            asi = st.number_input("Asistencias", 0, step=1, key=f"as_kda_{linea}")
        datos_kda.append({
            "Línea": linea,
            "Asesinatos": a,
            "Muertes": m,
            "Asistencias": asi,
            "Partida": partida_sel
        })
    if st.button("Guardar KDA"):
        df_kda = pd.DataFrame(datos_kda)
        st.session_state.kda_partidas.append(df_kda)
        st.success(f"KDA guardado para {partida_sel}")

# — Sección HISTORIAL —  
elif seccion == tr["historial"]:
    st.header(tr["historial"])
    if st.session_state.partidas or st.session_state.kda_partidas:
        if st.session_state.partidas:
            st.subheader("Partidas completas")
            hist = pd.concat(st.session_state.partidas, ignore_index=True)
            st.dataframe(hist)

        if st.session_state.kda_partidas:
            st.subheader("Registros solo de KDA")
            hist_kda = pd.concat(st.session_state.kda_partidas, ignore_index=True)
            st.dataframe(hist_kda)

            st.subheader("Datos combinados (por Partida y Línea)")
            try:
                df_partidas = pd.concat(st.session_state.partidas, ignore_index=True)
                df_kda = pd.concat(st.session_state.kda_partidas, ignore_index=True)
                df_merge = pd.merge(df_partidas, df_kda, on=["Partida", "Línea"], how="outer")
                st.dataframe(df_merge)
            except Exception as e:
                st.error(f"Error uniendo datos: {e}")
    else:
        st.info("No hay partidas registradas")

# — Sección PROMEDIO —
elif seccion == tr["promedio"]:
    st.header(tr["promedio"])
    if st.session_state.partidas:
        df = pd.concat(st.session_state.partidas, ignore_index=True)
        promedios = df.groupby("Línea")["Rendimiento"].mean().reset_index()
        st.dataframe(promedios)
    else:
        st.info("No hay datos para calcular promedios")

# — Sección FEEDBACK —
elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    if st.session_state.partidas:
        df = pd.concat(st.session_state.partidas, ignore_index=True)
        problemas = df.groupby("Línea")["Comentarios"].apply(lambda x: "; ".join(x)).reset_index()
        st.dataframe(problemas)
    else:
        st.info("No hay datos para feedback")

# — Sección RENDIMIENTO POR LÍNEA — CAMBIO: gráfico de barras a gráfico de líneas
elif seccion == tr["jugador"]:
    st.header(tr["jugador"])
    if st.session_state.partidas:
        df = pd.concat(st.session_state.partidas, ignore_index=True)
        linea_sel = st.selectbox("Selecciona la Línea", lineas)
        df_linea = df[df["Línea"] == linea_sel]
        if not df_linea.empty:
            chart = alt.Chart(df_linea).mark_line(point=True).encode(
                x=alt.X("Partida", sort=None),
                y="Rendimiento",
                tooltip=["Partida", "Rendimiento", "Comentarios"]
            ).properties(
                width=700,
                height=400,
                title=f"Rendimiento a lo largo de las partidas - {linea_sel}"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos para esta línea")
    else:
        st.info("No hay datos para mostrar")
