import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import base64

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
    msgs = []
    if fila["Daño Infligido"] < 20000:
        msgs.append("🔸 Aumenta tu farmeo y participa en peleas tempranas.")
    if fila["Participación (%)"] < 50:
        msgs.append("🔸 Sé más activo en objetivos de equipo.")
    if (fila["Asesinatos"] + fila["Asistencias"]) / max(1, fila["Muertes"]) < 1:
        msgs.append("🔸 Mejora tu posicionamiento para no morir tanto.")
    return "\n".join(msgs) or "✅ Buen equilibrio de métricas."

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
            com = st.text_area("Comentarios", key=f"com_{linea}")
            datos.append({
                "Línea": linea, "Oro": oro, "Daño Infligido": dano,
                "Daño Recibido": rec, "Participación (%)": part,
                "Asesinatos": a, "Muertes": m, "Asistencias": asi,
                "Comentarios": com
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
            x="Línea", y="value", color="variable"
        ).properties(title="Valores Numéricos", width=600)
        st.altair_chart(ch1, use_container_width=True)

        # Gráfico Altair de porcentajes
        pct = prom.melt("Línea", ["Participación (%)", "Rendimiento"])
        ch2 = alt.Chart(pct).mark_bar().encode(
            x="Línea", y="value", color="variable"
        ).properties(title="Porcentajes", width=600)
        st.altair_chart(ch2, use_container_width=True)
    else:
        st.info("No hay datos para calcular promedio")

# — Sección FEEDBACK DETALLADO —
elif seccion == tr["feedback"]:
    st.header(tr["feedback"])
    if st.session_state.partidas:
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        for ln in lineas:
            sub = df_all[df_all["Línea"] == ln]
            avg = sub["Rendimiento"].mean()
            st.subheader(ln)

            # Clamp y manejo de NaN
            bar = int(round(avg)) if pd.notna(avg) else 0
            bar = max(0, min(bar, 100))

            st.progress(bar)
            st.write(f"**Rendimiento Promedio:** {round(avg or 0, 2)}%")
            st.write(sugerencias(sub.iloc[-1]))
    else:
        st.info("Registra al menos una partida")

# — Sección RENDIMIENTO POR JUGADOR —
elif seccion == tr["jugador"]:
    st.header(tr["jugador"])
    if st.session_state.partidas:
        seleccionado = st.selectbox("Selecciona línea", lineas)
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        df_line = df_all[df_all["Línea"] == seleccionado]
        fig, ax = plt.subplots()
        ax.plot(df_line["Partida"], df_line["Rendimiento"], marker='o')
        ax.set_title(f"Rendimiento {seleccionado}")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("No hay datos para graficar")

# — Exportar a HTML corregido —
st.sidebar.markdown("---")
if st.sidebar.button(tr["exportar"]):
    if st.session_state.partidas:
        # Consolidar y calcular promedios
        df_all = pd.concat(st.session_state.partidas, ignore_index=True)
        prom = df_all.groupby("Línea").mean(numeric_only=True).reset_index()

        # Generar gráfico estático
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(prom["Línea"], prom["Rendimiento"])
        plt.xticks(rotation=45)
        plt.tight_layout()
        fp = "temp_promedio.png"
        fig.savefig(fp, bbox_inches="tight")
        plt.close(fig)

        # Convertir imagen a base64
        with open(fp, "rb") as imgf:
            img_b64 = base64.b64encode(imgf.read()).decode("utf-8")

        # Construir HTML
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte Diario de Rendimiento</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ text-align: center; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
                img {{ display: block; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <h1>{tr['promedio']}</h1>
            {prom.to_html(index=False, justify='center')}
            <h2 style="text-align: center;">{tr['grafico']}</h2>
            <img src="data:image/png;base64,{img_b64}" width="600" alt="Gráfico Promedio"/>
        </body>
        </html>
        """

        # Botón de descarga
        st.sidebar.success("HTML generado")
        st.sidebar.download_button(
            label="📥 Descargar Reporte HTML",
            data=html_content,
            file_name="reporte_diario.html",
            mime="text/html"
        )
    else:
        st.sidebar.warning("Nada para exportar")
