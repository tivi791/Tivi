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
    "kda": "📝 Registro KDA"  # --- CAMBIO: nuevo menú
}

# — Sidebar de navegación —
st.sidebar.title("Menú")
seccion = st.sidebar.radio("", [
    tr["registro"],
    tr["kda"],           # --- CAMBIO: nueva pestaña
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
if "kda_partidas" not in st.session_state:  # --- CAMBIO: lista para KDA por separado
    st.session_state.kda_partidas = []
if "kda_contador" not in st.session_state:
    st.session_state.kda_contador = 1

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
                # KDA eliminado de acá
                "Comentarios": "; ".join(comentarios)
            })
    if st.button(tr["guardar"]):
        df = pd.DataFrame(datos)
        df["Partida"] = f"Partida {st.session_state.contador}"
        df["Rendimiento"] = df.apply(calcular_puntaje, axis=1)
        st.session_state.partidas.append(df)
        st.session_state.contador += 1
        st.success("Partida guardada correctamente")

# — Nueva pestaña para registrar solo KDA —  # --- CAMBIO: pestaña KDA ---
elif seccion == tr["kda"]:
    st.header(tr["kda"])
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
            "Asistencias": asi
        })
    if st.button("Guardar KDA"):
        df_kda = pd.DataFrame(datos_kda)
        df_kda["Partida"] = f"Partida KDA {st.session_state.kda_contador}"
        st.session_state.kda_partidas.append(df_kda)
        st.session_state.kda_contador += 1
        st.success("KDA guardado correctamente")

# — Sección HISTORIAL — (mostramos ambos históricos separados)
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
    else:
        st.info("No hay partidas registradas")

# — Las demás secciones quedan igual —

elif seccion == tr["promedio"]:
    st.header(tr["promedio"])
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        prom = df_all.groupby("Línea").mean(numeric_only=True).reset_index()
        st.dataframe(prom)

        vals = prom.melt("Línea", ["Oro", "Daño Infligido", "Daño Recibido"])
        ch1 = alt.Chart(vals).mark_bar().encode(
            x="Línea", y="value", color="variable"
        ).properties(title="Valores Numéricos", width=600)
        st.altair_chart(ch1, use_container_width=True)

        pct = prom.melt("Línea", ["Participación (%)", "Rendimiento"])
        ch2 = alt.Chart(pct).mark_bar().encode(
            x="Línea", y="value", color="variable"
        ).properties(title="Porcentajes", width=600)
        st.altair_chart(ch2, use_container_width=True)
    else:
        st.info("No hay datos para calcular promedio")

elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        for ln in lineas:
            sub = df_all[df_all["Línea"] == ln]
            avg = sub["Rendimiento"].mean()
            st.subheader(ln)
            bar = int(round(avg)) if pd.notna(avg) else 0
            bar = max(0, min(bar, 100))
            st.progress(bar)
            st.write(f"**Rendimiento Promedio:** {round(avg,2)}%")
            suger = sub.apply(sugerencias, axis=1)
            for i, s in enumerate(suger):
                st.write(f"- Partida {i+1}: {s}")
    else:
        st.info("No hay partidas registradas")

elif seccion == tr["jugador"]:
    st.header(tr["jugador"])
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        lin = st.selectbox("Selecciona Línea", lineas)
        sub = df_all[df_all["Línea"] == lin]
        st.dataframe(sub)
    else:
        st.info("No hay datos para mostrar")

# — Exportar todo a HTML —
st.sidebar.markdown("---")
if st.sidebar.button(tr["exportar"]):
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        html = df_all.to_html()
        b64 = base64.b64encode(html.encode()).decode()
        href = f'<a href="data:file/html;base64,{b64}" download="partidas.html">Descargar partidas</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
    else:
        st.sidebar.info("No hay datos para exportar")
