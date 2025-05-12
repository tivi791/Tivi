import streamlit as st
import pandas as pd
import altair as alt

# Diccionario de usuarios y contraseñas
USUARIOS = {"Tivi": "2107", "Ghost": "203"}

# Función para iniciar sesión
def login(username, password):
    if username in USUARIOS:  # Verificar si el usuario existe
        if USUARIOS[username] == password:  # Verificar la contraseña
            return True
        else:
            return False, "Contraseña incorrecta"
    else:
        return False, "Usuario no encontrado"

# Configuración de la página
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

# Traducción según el idioma seleccionado
tr = T[idioma]

# Función de login
st.title(tr["titulo"])

username = st.text_input("Nombre de usuario")
password = st.text_input("Contraseña", type="password")

# Validación de login
if st.button("Iniciar sesión"):
    success, message = login(username, password)
    if success:
        st.session_state.logged_in = True
        st.success("Inicio de sesión exitoso!")
    else:
        st.session_state.logged_in = False
        st.error(f"Error: {message}")

if st.session_state.get("logged_in", False):
    # Aquí va el resto de tu código si el login es exitoso
    st.title(tr["titulo"])
    lineas = ["TOPLANER", "JUNGLA", "MIDLANER", "ADC", "SUPPORT"]
    datos = []

    # Tabs para organización visual
    tab1, tab2, tab3, tab4 = st.tabs([tr["registro"], tr["historial"], tr["promedio"], tr["feedback"]])

    with tab1:
        st.markdown("### 📌 Ingresa los datos por línea:")
        for linea in lineas:
            with st.expander(f"📍 {linea}", expanded=False):
                oro = st.number_input(f"{linea} - {tr['oro']}", min_value=0, step=100, key=f"oro_{linea}")
                dano_i = st.number_input(f"{linea} - {tr['dano_i']}", min_value=0, step=100, key=f"di_{linea}")
                dano_r = st.number_input(f"{linea} - {tr['dano_r']}", min_value=0, step=100, key=f"dr_{linea}")
                participacion = st.slider(f"{linea} - {tr['participacion']}", 0, 100, key=f"p_{linea}")
                asesinatos = st.number_input(f"{linea} - {tr['asesinatos']}", min_value=0, step=1, key=f"a_{linea}")
                muertes = st.number_input(f"{linea} - {tr['muertes']}", min_value=0, step=1, key=f"m_{linea}")
                asistencias = st.number_input(f"{linea} - {tr['asistencias']}", min_value=0, step=1, key=f"as_{linea}")

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

        if "partidas_dia" not in st.session_state:
            st.session_state.partidas_dia = []

        if st.button(tr["guardar"]):
            st.session_state.partidas_dia.append(df.copy())
            st.success(tr["guardado"])

    # El resto de las tabs sigue igual
else:
    st.warning("Por favor, inicia sesión para continuar.")
