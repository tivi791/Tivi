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
ROLES = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

if "partidas" not in st.session_state:
    st.session_state.partidas = []

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def autenticar_usuario(u, c):
    return USUARIOS.get(u) == c

def calificar_desempeno(vals, rol, maximos):
    """
    vals: [daño, recibido, oro, participación]
    maximos: dict con llaves 'Daño Infligido', 'Daño Recibido', ...
    """
    pct = lambda v, m: min((v / m) * 100, 100) if m else 0
    métricas = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {m: pct(v, maximos[m]) for m, v in zip(métricas, vals)}

    umbrales = {
        "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER":     {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER":    {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY":     {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT":     {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }

    mejoras = []
    textos = {
        "Daño Infligido":"Mejora farmeo y presión en línea.",
        "Oro Total":"Optimiza farmeo de minions y objetivos.",
        "Participación":"Participa más en peleas de equipo y visión."
    }
    for met, p in percentiles.items():
        if p < umbrales[rol].get(met, 0):
            mejoras.append(textos[met])

    if not mejoras:
        return f"Excelente desempeño como {rol}.", "Excelente", percentiles
    else:
        feedback = "Áreas de mejora:\n- " + "\n- ".join(mejoras)
        return feedback, "Bajo", percentiles

def exportar_pdf(resumen, fecha):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Resumen Diario - {fecha}", ln=True, align="C")
    for rol, datos in resumen.items():
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in datos.items():
            pdf.multi_cell(0, 6, f"{k}: {v}")
    return pdf.output(dest="S").encode("latin-1")

# ==============================
# LOGIN
# ==============================
st.sidebar.header("🔒 Login")
usuario = st.sidebar.text_input("Usuario")
clave   = st.sidebar.text_input("Clave", type="password")
if st.sidebar.button("Entrar"):
    if autenticar_usuario(usuario, clave):
        st.session_state.user = usuario
        st.sidebar.success(f"¡Hola, {usuario}!")
    else:
        st.sidebar.error("Credenciales inválidas")
if "user" not in st.session_state:
    st.stop()

# ==============================
# REGISTRO DE PARTIDA
# ==============================
st.header("Registrar Nueva Partida")
datos = {}
for rol in ROLES:
    st.subheader(rol)
    c1, c2, c3, c4 = st.columns(4)
    dano = c1.number_input("Daño Infligido", min_value=0, key=f"{rol}_d")
    recv = c2.number_input("Daño Recibido", min_value=0, key=f"{rol}_r")
    oro  = c3.number_input("Oro Total", min_value=0, key=f"{rol}_o")
    part = c4.number_input("Participación", min_value=0, max_value=100, key=f"{rol}_p")
    datos[rol] = {"dano": dano, "recibido": recv, "oro": oro, "participacion": part}

comentario = st.text_area("Comentario (opcional)")
if st.button("Guardar Partida"):
    st.session_state.partidas.append({
        "fecha": datetime.date.today(),
        "datos": datos,
        "comentario": comentario
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
        for rol in ROLES:
            for k, v in p["datos"][rol].items():
                acum[rol][k] += v
    n = len(hoy_partidas)

    # 2) Definir máximos fijos
    MAX = {"Daño Infligido":200000, "Daño Recibido":200000, "Oro Total":20000, "Participación":100}

    # 3) Calcular promedios y preparar DataFrame
    resumen = {}
    rows = []
    for rol in ROLES:
        prom = {
            "Daño Infligido": acum[rol]["dano"] / n,
            "Daño Recibido": acum[rol]["recibido"] / n,
            "Oro Total": acum[rol]["oro"] / n,
            "Participación": acum[rol]["participacion"] / n
        }
        feedback, cal, _ = calificar_desempeno(
            [prom["Daño Infligido"], prom["Daño Recibido"], prom["Oro Total"], prom["Participación"]],
            rol, MAX
        )
        resumen[rol] = {
            "Prom. Daño Infligido": int(prom["Daño Infligido"]),
            "Prom. Daño Recibido": int(prom["Daño Recibido"]),
            "Prom. Oro Total": int(prom["Oro Total"]),
            "Prom. Participación": int(prom["Participación"]),
            "Calificación": cal,
            "Feedback": feedback
        }
        for met, val in prom.items():
            rows.append({"Rol": rol, "Métrica": met, "Valor": val})

    df = pd.DataFrame(rows)

    # 4) Gráfico de barras agrupadas con Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Rol:N", title="Rol"),
        y=alt.Y("Valor:Q", title="Valor Promedio"),
        color=alt.Color("Métrica:N", title="Métrica"),
        column=alt.Column("Métrica:N", title=None)
    ).properties(width=150, height=250)
    st.altair_chart(chart, use_container_width=True)

    # 5) Tabla de promedios
    st.subheader("Tabla de Promedios")
    pivot = df.pivot(index="Rol", columns="Métrica", values="Valor").round(1)
    st.dataframe(pivot)

    # 6) Exportar a PDF
    if st.button("Exportar PDF"):
        pdf_bytes = exportar_pdf(resumen, hoy)
        st.download_button("Descargar PDF", pdf_bytes,
                           file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
