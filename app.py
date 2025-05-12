import streamlit as st
import datetime
from collections import defaultdict
import pandas as pd
import altair as alt
from fpdf import FPDF
import io

# ==============================
# CONFIGURACIÓN Y SESIÓN
# ==============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

USUARIOS = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

if "partidas" not in st.session_state:
    st.session_state.partidas = []

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def autenticar_usuario(u, c):
    return USUARIOS.get(u) == c

def calificar_desempeno(vals, rol, maximos):
    pct = lambda v, m: min((v / m)*100, 100) if m else 0
    names = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {n: pct(v, maximos[n]) for n, v in zip(names, vals)}
    umbrales = {
        "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER":     {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER":    {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY":     {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT":     {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }
    mejoras = []
    for m, p in percentiles.items():
        if p < umbrales[rol].get(m, 0):
            if m == "Daño Infligido":
                mejoras.append("Mejora farmeo y presión en línea.")
            if m == "Oro Total":
                mejoras.append("Optimiza farmeo de minions y objetivos.")
            if m == "Participación":
                mejoras.append("Participa más en peleas de equipo y visión.")
    if not mejoras:
        return f"Excelente desempeño como {rol}.", "Excelente", percentiles
    else:
        return "Áreas de mejora:\n- " + "\n- ".join(mejoras), "Bajo", percentiles

def exportar_pdf(resumen, fecha):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Resumen Diario - {fecha}", ln=True, align="C")
    for rol, datos in resumen.items():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in datos.items():
            pdf.multi_cell(0, 6, f"{k}: {v}")
    return pdf.output(dest='S').encode('latin-1')

# ==============================
# LOGIN
# ==============================
st.sidebar.header("🔒 Login")
user = st.sidebar.text_input("Usuario")
pwd  = st.sidebar.text_input("Clave", type="password")
if st.sidebar.button("Entrar"):
    if autenticar_usuario(user, pwd):
        st.session_state.user = user
        st.sidebar.success(f"¡Hola {user}!")
    else:
        st.sidebar.error("Credenciales inválidas")
if "user" not in st.session_state:
    st.stop()

# ==============================
# REGISTRO DE PARTIDA
# ==============================
st.header("Registrar Nueva Partida")
datos = {}
for rol in roles:
    st.subheader(rol)
    cols = st.columns(4)
    dano  = cols[0].number_input("Daño Infligido", min_value=0, key=f"{rol}_d")
    recv  = cols[1].number_input("Daño Recibido", min_value=0, key=f"{rol}_r")
    oro   = cols[2].number_input("Oro Total", min_value=0, key=f"{rol}_o")
    part  = cols[3].number_input("Participación", min_value=0, max_value=100, key=f"{rol}_p")
    datos[rol] = {"dano": dano, "recibido": recv, "oro": oro, "participacion": part}

coment = st.text_area("Comentario (opcional)")
if st.button("Guardar Partida"):
    st.session_state.partidas.append({
        "fecha": datetime.date.today(),
        "datos": datos,
        "coment": coment
    })
    st.success("Partida guardada ✔️")

# ==============================
# RESUMEN DIARIO
# ==============================
st.header("Resumen Diario")
hoy = datetime.date.today()
hoy_partidas = [p for p in st.session_state.partidas if p["fecha"] == hoy]
st.write(f"Partidas hoy: {len(hoy_partidas)}")

if hoy_partidas:
    # 1) Acumular estadísticas
    acum = defaultdict(lambda: {"dano":0, "recibido":0, "oro":0, "participacion":0})
    for p in hoy_partidas:
        for rol in roles:
            for k, v in p["datos"][rol].items():
                acum[rol][k] += v
    n = len(hoy_partidas)

    # 2) Calcular promedios y preparar DataFrame
    MAX = {"Daño Infligido":200000, "Daño Recibido":200000, "Oro Total":20000, "Participación":100}
    resumen = {}
    rows = []
    for rol in roles:
        prom = {
            "Daño Infligido": acum[rol]["dano"]/n,
            "Daño Recibido": acum[rol]["recibido"]/n,
            "Oro Total": acum[rol]["oro"]/n,
            "Participación": acum[rol]["participacion"]/n
        }
        msg, cal, _ = calificar_desempeno(
            [prom["Daño Infligido"], prom["Daño Recibido"], prom["Oro Total"], prom["Participación"]],
            rol, MAX
        )
        resumen[rol] = {
            "Prom. Daño Infligido": int(prom["Daño Infligido"]),
            "Prom. Daño Recibido": int(prom["Daño Recibido"]),
            "Prom. Oro Total": int(prom["Oro Total"]),
            "Prom. Participación": int(prom["Participación"]),
            "Calificación": cal,
            "Feedback": msg
        }
        for met, val in prom.items():
            rows.append({"Rol": rol, "Métrica": met, "Valor": val})

    df = pd.DataFrame(rows)

    # 3) Gráfico de barras agrupadas con Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Rol:N", title="Rol"),
        y=alt.Y("Valor:Q", title="Valor Promedio"),
        color=alt.Color("Métrica:N", title="Métrica"),
        column=alt.Column("Métrica:N", title=None)
    ).properties(width=150, height=250)
    st.altair_chart(chart, use_container_width=True)

    # 4) Tabla de promedios
    st.subheader("Tabla de Promedios")
    pivot = df.pivot(index="Rol", columns="Métrica", values="Valor").round(1)
    st.dataframe(pivot)

    # 5) Exportar a PDF
    if st.button("Exportar PDF"):
        pdf_bytes = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdf_bytes,
                           file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
