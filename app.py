import streamlit as st
from datetime import datetime
from statistics import mean

st.title("Evaluación diaria por rol - Honor of Kings")

roles = ["top", "jungla", "mid", "adc", "soporte"]
metricas = ["asesinatos", "muertes", "asistencias", "daño_infligido", "daño_recibido", "oro", "participación"]

if "partidas" not in st.session_state:
    st.session_state["partidas"] = []

with st.form("f1"):
    st.subheader("Registrar nueva partida")
    datos_juego = {}

    for rol in roles:
        datos_juego[rol] = {}
        st.markdown(f"**{rol.upper()}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            datos_juego[rol]["asesinatos"] = st.number_input(f"Asesinatos ({rol})", min_value=0, step=1, key=f"a_{rol}")
            datos_juego[rol]["muertes"] = st.number_input(f"Muertes ({rol})", min_value=0, step=1, key=f"m_{rol}")
        with col2:
            datos_juego[rol]["asistencias"] = st.number_input(f"Asistencias ({rol})", min_value=0, step=1, key=f"as_{rol}")
            datos_juego[rol]["oro"] = st.number_input(f"Oro ({rol})", min_value=0, max_value=15000, step=100, key=f"o_{rol}")
        with col3:
            datos_juego[rol]["daño_infligido"] = st.number_input(f"Daño infligido ({rol})", min_value=0, max_value=100000, step=1000, key=f"di_{rol}")
            datos_juego[rol]["daño_recibido"] = st.number_input(f"Daño recibido ({rol})", min_value=0, max_value=100000, step=1000, key=f"dr_{rol}")
            datos_juego[rol]["participación"] = st.slider(f"Participación en kills (%) ({rol})", 0, 100, key=f"p_{rol}")

    comentario_partida = st.text_area("Comentarios o incidencias del juego (opcional)", max_chars=300)

    submitted = st.form_submit_button("Guardar partida")
    if submitted:
        st.session_state["partidas"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "datos": datos_juego,
            "comentario": comentario_partida.strip()
        })
        st.success("Partida guardada correctamente.")

st.subheader("Análisis diario")
if st.session_state["partidas"]:
    hoy = datetime.now().strftime("%Y-%m-%d")
    hoy_partidas = [p for p in st.session_state["partidas"] if p["fecha"] == hoy]

    if hoy_partidas:
        acumulado = {rol: {m: 0 for m in metricas} for rol in roles}
        for partida in hoy_partidas:
            for rol in roles:
                for m in metricas:
                    acumulado[rol][m] += partida["datos"][rol][m]

        for rol in roles:
            prom = {m: acumulado[rol][m] / len(hoy_partidas) for m in metricas}

            msg = f"🎯 **{rol.upper()}**\n"
            if prom["muertes"] > 5:
                msg += "- Estás muriendo mucho. Revisa tu posicionamiento y toma de decisiones.\n"
            if prom["participación"] < 50:
                msg += "- Tu participación es baja. Intenta estar más presente en peleas grupales.\n"
            if prom["oro"] < 8000:
                msg += "- Oro por partida bajo. Mejora tu farmeo o toma mejores objetivos.\n"
            if prom["daño_infligido"] < 30000:
                msg += "- El daño infligido es bajo. Asegúrate de impactar en las peleas.\n"

            comentarios_relevantes = [
                p.get("comentario", "") for p in hoy_partidas if len(p.get("comentario", "")) > 20
            ]
            feedback_extra = ""
            if comentarios_relevantes:
                for c in comentarios_relevantes:
                    cl = c.lower()
                    if "afk" in cl:
                        feedback_extra += "- Hubo un jugador ausente (AFK). Considerar estrategias de recuperación.\n"
                    if "visión" in cl or "vision" in cl:
                        feedback_extra += "- Se mencionó falta de visión en el mapa. Mejora el uso de centinelas.\n"
                    if "tilt" in cl or "mal ambiente" in cl:
                        feedback_extra += "- Se detectó desmotivación o mal ambiente. Refuerza comunicación positiva.\n"
                    if "presión" in cl:
                        feedback_extra += "- Se mencionó presión en línea. Evalúa pedir apoyo o jugar más seguro.\n"

            if feedback_extra:
                msg += "\n📌 **Comentarios detectados:**\n" + feedback_extra

            st.markdown(msg)
    else:
        st.info("No hay partidas registradas hoy.")
else:
    st.info("Aún no se han registrado partidas.")
