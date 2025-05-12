import streamlit as st
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import io

# ==============================
# CONFIGURACIÓN
# ==============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

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
    # vals = [dano, recibido, oro, participacion]
    pct = lambda v, m: min((v / m) * 100, 100) if m else 0
    names = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {n: pct(v, maximos[n]) for n, v in zip(names, vals)}

    umbr = {
      "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
      # ... etc
    }
    umbrales = umbr[rol]
    mejoras = []
    for met, p in percentiles.items():
        if p < umbrales.get(met,0):
            if met=="Daño Infligido":   mejoras.append("Mejora farmeo/presión")
            if met=="Oro Total":        mejoras.append("Optimiza farmeo de objetivos")
            if met=="Participación":    mejoras.append("Participa más en equipo")
    if not mejoras:
        return f"Excelente como {rol}.", "Excelente", percentiles
    else:
        return "Áreas de mejora:\n- " + "\n- ".join(mejoras), "Bajo", percentiles

def generar_grafico(pct, rol):
    cats = list(pct.keys())
    vals = list(pct.values())
    vals += vals[:1]
    ang = [n/float(len(cats))*2*pi for n in range(len(cats))]
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
    ax.plot(ang, vals, color="#FFD700", lw=2)
    ax.fill(ang, vals, color="#FFD700", alpha=0.3)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(cats, color="white", fontsize=10)
    ax.set_yticks([20,40,60,80,100]); ax.set_yticklabels(["20%","40%","60%","80%","100%"], color="grey", size=8)
    ax.set_ylim(0,100); ax.set_title(rol, color="white")
    buf = io.BytesIO(); plt.savefig(buf, format="png", facecolor="#0a0a0a", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return buf

def exportar_pdf(res, fecha):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(0,10, f"Resumen Diario - {fecha}", ln=True, align="C")
    for rol, d in res.items():
        pdf.ln(5); pdf.set_font("Arial","B",12); pdf.cell(0,8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k,v in d.items():
            pdf.multi_cell(0,6, f"{k}: {v}")
    return pdf.output(dest="S").encode("latin-1")

# ==============================
# LOGIN
# ==============================
st.sidebar.header("🔒 Login")
u = st.sidebar.text_input("Usuario")
c = st.sidebar.text_input("Clave", type="password")
if st.sidebar.button("Entrar"):
    if autenticar_usuario(u,c):
        st.session_state.user = u; st.sidebar.success(f"¡Hola {u}!")
    else:
        st.sidebar.error("Credenciales incorrectas")
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
    st.session_state.partidas.append({"fecha": datetime.date.today(), "datos": datos, "coment": coment})
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
        for rol in roles:
            d = p["datos"][rol]
            for k in d: acum[rol][k]+= d[k]
    # calcular máximos OBSERVADOS para cada métrica
    max_obs = {"dano":0,"recibido":0,"oro":0,"participacion":0}
    for rol in roles:
        for k in max_obs:
            max_obs[k] = max(max_obs[k], acum[rol][k]/len(hj))
    # construir un dict con llaves de nombre
    maximos = {
        "Daño Infligido": max_obs["dano"],
        "Daño Recibido": max_obs["recibido"],
        "Oro Total": max_obs["oro"],
        "Participación": 100
    }

    resumen = {}
    for rol in roles:
        stats = acum[rol]; n = len(hj)
        prom = [stats["dano"]/n, stats["recibido"]/n, stats["oro"]/n, stats["participacion"]/n]
        msg, cal, pct = calificar_desempeno(prom, rol, maximos)
        resumen[rol]={
            "Prom. Daño": int(prom[0]),
            "Prom. Recibido": int(prom[1]),
            "Prom. Oro": int(prom[2]),
            "Prom. Part.": int(prom[3]),
            "Calificación": cal,
            "Feedback": msg
        }
        st.image(generar_grafico(pct, rol))

    st.subheader("Detalle")
    for rol, d in resumen.items():
        st.markdown(f"**{rol}**")
        for k,v in d.items():
            st.write(f"- {k}: {v}")

    if st.button("Exportar PDF"):
        pdf = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdf, file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
