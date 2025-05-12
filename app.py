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
    umbr = {
        "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER":     {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER":    {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY":     {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT":     {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }
    mejoras = []
    for m, p in percentiles.items():
        if p < umbr[rol].get(m,0):
            if m=="Daño Infligido": mejoras.append("Mejora farmeo/presión")
            if m=="Oro Total":      mejoras.append("Optimiza farmeo de objetivos")
            if m=="Participación":  mejoras.append("Participa más en equipo")
    if not mejoras:
        return f"Excelente desempeño como {rol}.", "Excelente", percentiles
    else:
        return "Áreas de mejora:\n- " + "\n- ".join(mejoras), "Bajo", percentiles

def exportar_pdf(resumen, fecha):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(0,10, f"Resumen Diario - {fecha}", ln=True, align="C")
    for rol, d in resumen.items():
        pdf.ln(5); pdf.set_font("Arial","B",12); pdf.cell(0,8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k,v in d.items():
            pdf.multi_cell(0,6, f"{k}: {v}")
    return pdf.output(dest="S").encode("latin-1")

# ==============================
# LOGIN
# ==============================
st.sidebar.header("🔒 Login")
user = st.sidebar.text_input("Usuario")
pwd  = st.sidebar.text_input("Clave", type="password")
if st.sidebar.button("Entrar"):
    if autenticar_usuario(user,pwd):
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
    dano = cols[0].number_input("Daño Infligido", min_value=0, key=f"{rol}_d")
    recv = cols[1].number_input("Daño Recibido", min_value=0, key=f"{rol}_r")
    oro  = cols[2].number_input("Oro Total", min_value=0, key=f"{rol}_o")
    part = cols[3].number_input("Participación", min_value=0, max_value=100, key=f"{rol}_p")
    datos[rol] = {"dano":dano,"recibido":recv,"oro":oro,"participacion":part}

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
hj = [p for p in st.session_state.partidas if p["fecha"]==hoy]
st.write(f"Partidas hoy: {len(hj)}")

if hj:
    acum = defaultdict(lambda: {"dano":0,"recibido":0,"oro":0,"participacion":0})
    for p in hj:
        for r in roles:
            for k,v in p["datos"][r].items():
                acum[r][k] += v
    n = len(hj)
    MAX = {"Daño Infligido":200000,"Daño Recibido":200000,"Oro Total":20000,"Participación":100}
    resumen = {}
    rows = []
    for r in roles:
        prom = {
            "Daño Infligido": acum[r]["dano"]/n,
            "Daño Recibido": acum[r]["recibido"]/n,
            "Oro Total": acum[r]["oro"]/n,
            "Participación": acum[r]["participacion"]/n
        }
        resumen[r] = prom
        for met,val in prom.items():
            rows.append({"Rol":r, "Métrica":met, "Valor":val})

    df = pd.DataFrame(rows)

    # — Gráfico de barras agrupadas Altair —
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Rol:N", title="Rol"),
        y=alt.Y("Valor:Q", title="Valor Promedio"),
        color=alt.Color("Métrica:N", title="Métrica"),
        column=alt.Column("Métrica:N", title=None)
    ).properties(width=150, height=250)
    st.altair_chart(chart, use_container_width=True)

    # Tabla de promedios
    st.subheader("Tabla de Promedios")
    pivot = df.pivot(index="Rol", columns="Métrica", values="Valor").round(1)
    st.dataframe(pivot)

    # Exportar PDF
    if st.button("Exportar PDF"):
        pdf_bytes = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdf_bytes,
                           file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
