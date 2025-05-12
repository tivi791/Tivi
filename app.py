import streamlit as st
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import io

# ==============================
# CONFIGURACIÓN Y SESIÓN
# ==============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

# Datos de autenticación
USUARIOS = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# Inicializar estado
if "partidas" not in st.session_state:
    st.session_state.partidas = []

# ==============================
# FUNCIONES
# ==============================
def autenticar_usuario(usuario, clave):
    return USUARIOS.get(usuario) == clave

def calificar_desempeno(valores, rol, maximos):
    # valores: [dano, recibido, oro, participacion]
    pct = lambda v, m: min((v / m) * 100, 100) if m else 0
    names = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {n: pct(v, maximos[n]) for n, v in zip(names, valores)}

    umbrales = {
        "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER":     {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER":    {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY":     {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT":     {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }

    mejoras = []
    for métrica, pct_val in percentiles.items():
        if pct_val < umbrales[rol].get(métrica, 0):
            if métrica == "Daño Infligido":
                mejoras.append("Mejora tu farmeo y presiona más en línea.")
            if métrica == "Oro Total":
                mejoras.append("Optimiza tu farmeo de minions y objetivos.")
            if métrica == "Participación":
                mejoras.append("Participa más en peleas de equipo y visión del mapa.")

    if not mejoras:
        return f"Excelente desempeño como {rol}.", "Excelente", percentiles
    else:
        texto = "Áreas de mejora:\n- " + "\n- ".join(mejoras)
        return texto, "Bajo", percentiles

def generar_grafico(percentiles, rol, maximos):
    categorias = list(percentiles.keys())
    valores = list(percentiles.values())
    valores += valores[:1]
    ang = [n/float(len(categorias))*2*pi for n in range(len(categorias))]
    ang += ang[:1]

    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
    ax.plot(ang, valores, color='#FFD700', linewidth=2)
    ax.fill(ang, valores, color='#FFD700', alpha=0.3)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(categorias, color='white', fontsize=10)
    ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels(['20%','40%','60%','80%','100%'], color='grey', size=8)
    ax.set_ylim(0,100)
    ax.set_title(f"{rol}", color='white')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    plt.close(fig)
    buf.seek(0)
    return buf

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
        for k,v in datos.items():
            line = f"{k}: {v}"
            pdf.multi_cell(0, 6, line)
    return pdf.output(dest='S').encode('latin-1')

# ==============================
# LAYOUT
# ==============================
# Login
st.sidebar.header("🔒 Inicio de Sesión")
u = st.sidebar.text_input("Usuario")
c = st.sidebar.text_input("Contraseña", type="password")
if st.sidebar.button("Entrar"):
    if autenticar_usuario(u,c):
        st.session_state.user = u
        st.sidebar.success(f"Bienvenido, {u}!")
    else:
        st.sidebar.error("Credenciales inválidas")

if "user" not in st.session_state:
    st.stop()

# Registro de partidas
st.header("Registrar Nueva Partida")
datos = {}
for rol in roles:
    st.subheader(rol)
    cols = st.columns(4)
    dano = cols[0].number_input("Daño Infligido", min_value=0, key=f"{rol}_d")
    recibido = cols[1].number_input("Daño Recibido", min_value=0, key=f"{rol}_r")
    oro = cols[2].number_input("Oro Total", min_value=0, key=f"{rol}_o")
    part = cols[3].number_input("Participación", min_value=0, max_value=100, key=f"{rol}_p")
    datos[rol] = {"dano":dano, "recibido":recibido, "oro":oro, "participacion":part}

comentario = st.text_area("Comentario (opcional)")
if st.button("Guardar Partida"):
    st.session_state.partidas.append({
        "fecha": datetime.date.today(),
        "datos": datos,
        "comentario": comentario
    })
    st.success("Partida guardada ✔️")

# Resumen diario
st.header("Resumen Diario")
hoy = datetime.date.today()
hoy_partidas = [p for p in st.session_state.partidas if p["fecha"]==hoy]
st.write(f"Partidas hoy: {len(hoy_partidas)}")

if hoy_partidas:
    acumulado = defaultdict(lambda: {"dano":0,"recibido":0,"oro":0,"participacion":0})
    for p in hoy_partidas:
        for rol in roles:
            d = p["datos"][rol]
            acumulado[rol]["dano"] += d["dano"]
            acumulado[rol]["recibido"] += d["recibido"]
            acumulado[rol]["oro"] += d["oro"]
            acumulado[rol]["participacion"] += d["participacion"]

    resumen = {}
    MAXIMOS = {"Daño Infligido":200000,"Daño Recibido":200000,"Oro Total":20000,"Participación":100}
    for rol in roles:
        stats = acumulado[rol]
        n = len(hoy_partidas)
        prom = {"dano":stats["dano"]/n, "recibido":stats["recibido"]/n,
                "oro":stats["oro"]/n, "participacion":stats["participacion"]/n}
        vals = [prom["dano"], prom["recibido"], prom["oro"], prom["participacion"]]
        msg, cal, pct = calificar_desempeno(vals, rol, MAXIMOS)
        resumen[rol] = {
            "Prom. Daño Infligido": int(prom["dano"]),
            "Prom. Daño Recibido": int(prom["recibido"]),
            "Prom. Oro Total": int(prom["oro"]),
            "Prom. Participación": int(prom["participacion"]),
            "Calificación": cal,
            "Feedback": msg
        }
        buf = generar_grafico(pct, rol, MAXIMOS)
        st.image(buf)

    st.subheader("Detalles")
    for rol, datos in resumen.items():
        st.markdown(f"**{rol}**")
        for k,v in datos.items():
            st.write(f"- {k}: {v}")

    if st.button("Exportar PDF"):
        pdf_bytes = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdf_bytes, file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
