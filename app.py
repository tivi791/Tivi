import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
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
    "rendimiento": "Rendimiento (%)"
}

# — Sidebar de navegación —
st.sidebar.title("Menú")
seccion = st.sidebar.radio("", [
    tr["registro"],
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

# — Lista de problemas comunes para comentarios —
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

# — Pesos por rol para el cálculo de puntaje —
pesos = {
    "TOPLANER": {"oro":0.2, "dano":0.3, "part":0.2, "kda":0.3},
    "JUNGLA":   {"oro":0.2, "dano":0.25,"part":0.25,"kda":0.3},
    "MIDLANER": {"oro":0.2, "dano":0.3, "part":0.2, "kda":0.3},
    "ADC":      {"oro":0.2, "dano":0.2, "part":0.3, "kda":0.3},
    "SUPPORT":  {"oro":0.1, "dano":0.1, "part":0.4, "kda":0.4}
}

# — Funciones centrales —

def calcular_puntaje(fila):
    rol = fila["Línea"]
    p = pesos[rol]
    kda = (fila["Asesinatos"] + fila["Asistencias"]) / max(1, fila["Muertes"])
    val_oro = fila["Oro"] / 15000
    val_dano = fila["Daño Infligido"] / 100000
    val_part = fila["Participación (%)"] / 100
    eficiencia = (
        val_oro * p["oro"] +
        val_dano * p["dano"] +
        val_part * p["part"] +
        (kda / 5) * p["kda"]
    )
    return round(eficiencia * 100, 2)

def sugerencias(fila):
    # Feedback multidimensional
    feedback = {
        "Farmeo": [],
        "Visión": [],
        "Posicionamiento": [],
        "Objetivos": [],
        "Teamfights": [],
        "Comunicación": []
    }
    # Farmeo
    if fila["Daño Infligido"] < 20000:
        feedback["Farmeo"].append("🔸 Aumenta tu farmeo y participa en peleas tempranas.")
    # Visión
    if fila["Participación (%)"] < 50:
        feedback["Visión"].append("🔸 Sé más activo en objetivos de equipo.")
    # Posicionamiento
    if (fila["Asesinatos"] + fila["Asistencias"]) / max(1, fila["Muertes"]) < 1:
        feedback["Posicionamiento"].append("🔸 Mejora tu posicionamiento para no morir tanto.")
    # Otros
    feedback["Objetivos"].append("🔸 Sé más eficiente en los objetivos.")
    feedback["Teamfights"].append("🔸 Coordina mejor tus teamfights.")
    feedback["Comunicación"].append("🔸 Mantén una mejor comunicación con el equipo.")

    # Asignar prioridad
    prioridades = {
        "Farmeo": "Alta",
        "Visión": "Alta",
        "Posicionamiento": "Alta",
        "Objetivos": "Media",
        "Teamfights": "Media",
        "Comunicación": "Baja"
    }

    # Construir las sugerencias
    suggestions_text = ""
    for area, msgs in feedback.items():
        if msgs:
            suggestions_text += f"**{area} ({prioridades[area]}):**\n"
            for msg in msgs:
                suggestions_text += f"  {msg}\n"
    
    return suggestions_text if suggestions_text else "✅ Buen equilibrio de métricas."

# — Sección REGISTRO —
if seccion == tr["registro"]:
    st.header(tr["registro"])
    datos = []
    for linea in lineas:
        with st.expander(linea):
            oro = st.number_input("Oro", 0, step=100, key=f"oro_{linea}")
            dano = st.number_input("Daño Infligido", 0, step=100, key=f"dano_{linea}")
            rec = st.number_input("Daño Recibido", 0, step=100, key=f"dr_{linea}")
            part = st.slider("Participación %", 0, 100, key=f"part_{linea}")
            a = st.number_input("Asesinatos", 0, step=1, key=f"a_{linea}")
            m = st.number_input("Muertes", 0, step=1, key=f"m_{linea}")
            asi = st.number_input("Asistencias", 0, step=1, key=f"as_{linea}")
            # multiselect de problemas comunes + otro
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
                "Asesinatos": a, "Muertes": m, "Asistencias": asi,
                "Comentarios": "; ".join(comentarios)
            })
    if st.button(tr["guardar"]):
        df = pd.DataFrame(datos)
        df["Partida"] = f"Partida {st.session_state.contador}"
        df["Rendimiento"] = df.apply(calcular_puntaje, axis=1)
        st.session_state.partidas.append(df)
        st.session_state.contador += 1
        st.success("Partida guardada correctamente")

# — Sección HISTORIAL —
elif seccion == tr["historial"]:
    st.header(tr["historial"])
    if st.session_state.partidas:
        hist = pd.concat(st.session_state.partidas, ignore_index=True)
        st.dataframe(hist)
    else:
        st.info("No hay partidas registradas")

# — Sección PROMEDIO y GRÁFICOS —
elif seccion == tr["promedio"]:
    st.header(tr["promedio"])
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        prom = df_all.groupby("Línea").mean(numeric_only=True).reset_index()
        st.dataframe(prom)

        # Gráfico Altair de valores
        vals = prom.melt("Línea", ["Oro", "Daño Infligido", "Daño Recibido"])
        ch1 = alt.Chart(vals).mark_bar().encode(
            x="variable:N",
            y="value:Q",
            color="Línea:N",
            column="Línea:N"
        ).properties(width=100)
        st.altair_chart(ch1, use_container_width=True)
    else:
        st.info("No hay partidas registradas")

# — Sección Feedback —
elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    st.write(sugerencias({"Oro": 1500, "Daño Infligido": 15000, "Participación (%)": 60, "Asesinatos": 10, "Muertes": 5, "Asistencias": 8, "Línea": "TOPLANER"}))
