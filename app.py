import streamlit as st
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
import io

# ==============================
# CONFIGURACIÓN Y SESIÓN
# ==============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

# Datos de autenticación
USUARIOS = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

if "partidas" not in st.session_state:
    st.session_state.partidas = []

# ==============================
# FUNCIONES
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
            if m=="Daño Infligido": mejoras.append("Mejora tu farmeo/presión")
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
    return pdf.output(dest='S').encode('latin-1')

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
# REGISTRO PARTIDA
# ==============================
st.header("Registrar Nueva Partida")
datos = {}
for rol in roles:
    st.subheader(rol)
    cols = st.columns(4)
    dano = cols[0].number_input("Daño Infligido", min_value=0, key=f"{rol}_d")
    recv = cols[1].number_input("Daño Recibido", min_value=0, key=f"{rol}_r")
    oro  = cols[2].number_input("Oro Total", min_value=0, key=f"{rol}_o")
    part= cols[3].number_input("Participación", min_value=0, max_value=100, key=f"{rol}_p")
    datos[rol] = {"dano":dano,"recibido":recv,"oro":oro,"participacion":part}

coment = st.text_area("Comentario (opcional)")
if st.button("Guardar Partida"):
    st.session_state.partidas.append({
        "fecha": datetime.date.today(), "datos": datos, "coment": coment
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
    # 1) Acumular y calcular promedios
    acum = defaultdict(lambda: {"dano":0,"recibido":0,"oro":0,"participacion":0})
    for p in hj:
        for r in roles:
            d = p["datos"][r]
            for k in acum[r]:
                acum[r][k] += d[k]
    n = len(hj)
    # 2) Definir máximos fijos
    MAX = {"Daño Infligido":200000,"Daño Recibido":200000,"Oro Total":20000,"Participación":100}
    resumen = {}
    for r in roles:
        prom = {k:acum[r][k]/n for k in acum[r]}
        vals = [prom["dano"],prom["recibido"],prom["oro"],prom["participacion"]]
        msg, cal, pct = calificar_desempeno(vals, r, MAX)
        resumen[r] = {
            "Prom. Daño Infligido":int(prom["dano"]),
            "Prom. Daño Recibido":int(prom["recibido"]),
            "Prom. Oro Total":int(prom["oro"]),
            "Prom. Participación":int(prom["participacion"]),
            "Calificación":cal,
            "Feedback":msg
        }
        # 3) Preparar DataFrame y graficar con líneas
        df = pd.DataFrame(hj).apply(lambda x: x["datos"][r], axis=1).tolist()
        df = pd.DataFrame(df)
        df.index = [f"Match {i+1}" for i in range(n)]
        df.columns = ["Daño Infligido","Daño Recibido","Oro Total","Participación"]
        st.subheader(r)
        st.line_chart(df)

    # Mostrar detalles y PDF
    st.subheader("Detalle")
    for r,d in resumen.items():
        st.markdown(f"**{r}**")
        for k,v in d.items():
            st.write(f"- {k}: {v}")

    if st.button("Exportar PDF"):
        pdfb = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdfb, file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
