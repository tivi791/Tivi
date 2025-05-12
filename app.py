import streamlit as st
import datetime
from collections import defaultdict

# Configurar la página
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="centered")
st.title("\U0001F3C6 WOLF SEEKERS E-SPORTS - Registro Diario")

# Roles personalizados
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# Datos en sesión
if "partidas" not in st.session_state:
    st.session_state.partidas = []

# Función para calificar el desempeño de un jugador
def calificar_desempeno(dano, recibido, oro, participacion):
    puntaje = 0
    if dano > 50000:
        puntaje += 1
    if recibido > 30000:
        puntaje += 1
    if oro > 10000:
        puntaje += 1
    if participacion > 50:
        puntaje += 1

    if puntaje >= 3:
        return "Alto"
    elif puntaje == 2:
        return "Medio"
    else:
        return "Bajo"

# Función para generar feedback
def generar_feedback(dano, oro, participacion):
    feedback = []
    if dano < 40000:
        feedback.append("Aumenta tu daño infligido: mejora tu farmeo y presiona más en línea.")
    if oro < 8000:
        feedback.append("Optimiza tu farmeo de minions y objetivos para mejorar tu oro.")
    if participacion < 40:
        feedback.append("Participa más en peleas de equipo y visión del mapa.")
    return feedback

# Registro de nueva partida
st.header("Registrar Nueva Partida")
nueva_partida = {}

for rol in roles:
    st.subheader(rol)
    dano = st.number_input(f"Daño Infligido ({rol})", min_value=0)
    recibido = st.number_input(f"Daño Recibido ({rol})", min_value=0)
    oro = st.number_input(f"Oro Total ({rol})", min_value=0)
    participacion = st.number_input(f"Participación ({rol})", min_value=0)
    nueva_partida[rol] = {
        "dano": dano,
        "recibido": recibido,
        "oro": oro,
        "participacion": participacion
    }

comentario = st.text_area("Comentario del equipo sobre esta partida (opcional)")

if st.button("Guardar Partida"):
    st.session_state.partidas.append({"fecha": datetime.date.today(), "datos": nueva_partida, "comentario": comentario})
    st.success("Partida guardada ✔️")

# Mostrar resumen diario
st.header("Resumen Diario")
hoy = datetime.date.today()
hoy_partidas = [p for p in st.session_state.partidas if p["fecha"] == hoy]
st.write(f"Partidas hoy: {len(hoy_partidas)}")

if not hoy_partidas:
    st.info("No se registraron partidas hoy.")
else:
    acumulado = defaultdict(lambda: {"dano": 0, "recibido": 0, "oro": 0, "participacion": 0})

    for partida in hoy_partidas:
        for rol in roles:
            datos = partida["datos"][rol]
            acumulado[rol]["dano"] += datos["dano"]
            acumulado[rol]["recibido"] += datos["recibido"]
            acumulado[rol]["oro"] += datos["oro"]
            acumulado[rol]["participacion"] += datos["participacion"]

    for rol in roles:
        st.subheader(rol)
        stats = acumulado[rol]
        promedio_dano = stats["dano"] // len(hoy_partidas)
        promedio_recibido = stats["recibido"] // len(hoy_partidas)
        promedio_oro = stats["oro"] // len(hoy_partidas)
        promedio_part = stats["participacion"] // len(hoy_partidas)

        st.write(f"{promedio_dano}")
        calificacion = calificar_desempeno(promedio_dano, promedio_recibido, promedio_oro, promedio_part)
        st.write(f"Calificación: {calificacion}")

        feedback = generar_feedback(promedio_dano, promedio_oro, promedio_part)
        if feedback:
            st.write("Feedback detallado:")
            st.markdown("\n".join([f"- {f}" for f in feedback]))

    # Análisis básico de comentarios
    comentarios_relevantes = [p.get("comentario", "") for p in hoy_partidas if len(p.get("comentario", "")) > 20]

    if comentarios_relevantes:
        st.subheader("\U0001F9E0 Comentarios detectados:")
        for comentario in comentarios_relevantes:
            analisis = []
            if "afk" in comentario.lower():
                analisis.append("⚠️ Se reportó un jugador AFK.")
            if "visión" in comentario.lower() or "ward" in comentario.lower():
                analisis.append("👁️ Falta de visión mencionada. Refuerza uso de sentinelas y control de mapa.")
            if "tilt" in comentario.lower() or "flame" in comentario.lower():
                analisis.append("😠 Posible mal ambiente. Refuerza comunicación positiva y ánimo del equipo.")
            if analisis:
                st.markdown(f"**Comentario:** _{comentario}_")
                st.markdown("\n".join(analisis))
