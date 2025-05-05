# app.py

import streamlit as st
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import pandas as pd
import io
import base64
from datetime import datetime

# =============================
# CONFIGURACIÓN Y AUTENTICACIÓN
# =============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")

USUARIOS = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}

def autenticar_usuario(usuario, clave):
    return USUARIOS.get(usuario) == clave

# =============================
# FUNCIONES DE NEGOCIO
# =============================
def calificar_desempeno(valores_norm, rol, maximos):
    # valores_norm: [prom_dmg, prom_rec, prom_oro, prom_part]
    pct = lambda v, m: (v / m) * 100 if m else 0
    names = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {n: pct(v, maximos[n]) for n, v in zip(names, valores_norm)}

    # Umbrales por rol
    umbrales = {
        "TOPLANER":    {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER":     {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER":    {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY":     {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT":     {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }

    mejoras = []
    for métrica, pct_val in percentiles.items():
        # No evaluamos daño recibido, solo lo mostramos
        if métrica in umbrales[rol] and pct_val < umbrales[rol][métrica]:
            if métrica == "Daño Infligido":
                mejoras.append("Aumenta tu daño infligido: mejora tu farmeo y presiona más en línea.")
            if métrica == "Oro Total":
                mejoras.append("Optimiza tu farmeo de minions y objetivos para mejorar tu oro.")
            if métrica == "Participación":
                mejoras.append("Participa más en peleas de equipo y visión del mapa.")

    # Siempre sugerimos fortalecer debilitados
    if not mejoras:
        mensaje = f"Excelente desempeño como {rol}. Sigue manteniendo tu nivel alto en todas las métricas."
        cal = "Excelente"
    else:
        mensaje = f"Áreas de mejora como {rol}:\n• " + "\n• ".join(mejoras)
        cal = "Bajo"

    return mensaje, cal, percentiles

def generar_grafico(datos, titulo, maximos):
    categorias = list(datos.keys())
    valores = [datos[c] for c in categorias]
    valores_norm = [(v / maximos[c])*100 if maximos[c] else 0 for v,c in zip(valores,categorias)]
    valores_norm += valores_norm[:1]
    ang = [n/float(len(categorias))*2*pi for n in range(len(categorias))]
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(ang, valores_norm, color='#FFD700', linewidth=2)
    ax.fill(ang, valores_norm, color='#FFD700', alpha=0.3)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(categorias, color='white', fontsize=12)
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    plt.close(fig)
    return buf

def exportar_pdf(resumen, fecha, equipo="WOLF SEEKERS E-SPORTS"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Resumen Diario - {fecha}", ln=True, align="C")
    pdf.cell(0, 10, f"Equipo: {equipo}", ln=True, align="C")
    for rol, datos in resumen.items():
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k,v in datos.items():
            pdf.multi_cell(0, 6, f"{k}: {v}")
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

def exportar_excel(partidas):
    registros = []
    roles = ["TOPLANER","JUNGLER","MIDLANER","ADCARRY","SUPPORT"]
    for p in partidas:
        for i, rol in enumerate(roles):
            fila = p["datos"][i].copy()
            fila["Fecha"] = p["fecha"]
            fila["Rol"] = rol
            registros.append(fila)
    df = pd.DataFrame(registros)
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf

# =============================
# ESTILOS
# =============================
st.markdown("""
<style>
body, .css-1d391kg { background-color: #0a0a0a; color: white; }
.stButton>button { background-color: #FFD700; color: black; font-weight: bold; }
input, .stNumberInput input { background-color: #1e1e1e; color: white; }
</style>
""", unsafe_allow_html=True)

# =============================
# INTERFAZ
# =============================
st.title("🏆 WOLF SEEKERS E-SPORTS - Registro Diario")

# Login
usuario = st.sidebar.text_input("Usuario")
clave   = st.sidebar.text_input("Contraseña", type="password")
if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario, clave):
        st.session_state["auth"] = True
        st.sidebar.success("¡Sesión iniciada!")
    else:
        st.sidebar.error("Credenciales incorrectas.")

if not st.session_state.get("auth"):
    st.stop()

# Registro de partida
roles = ["TOPLANER","JUNGLER","MIDLANER","ADCARRY","SUPPORT"]
metricas = ["Daño Infligido","Daño Recibido","Oro Total","Participación"]
if "partidas" not in st.session_state:
    st.session_state["partidas"] = []

st.header("Registrar Nueva Partida")
with st.form("f1"):
    datos_juego = []
    for rol in roles:
        st.subheader(rol)
        cols = st.columns(4)
        vals = {}
        for i, met in enumerate(metricas):
            vals[met] = cols[i].number_input(f"{met} ({rol})", min_value=0, key=f"{rol}_{met}")
        datos_juego.append(vals)
    if st.form_submit_button("Guardar Partida"):
        st.session_state["partidas"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "datos": datos_juego
        })
        st.success("Partida guardada ✔️")

# Resumen diario
st.header("Resumen Diario")
hoy = datetime.now().strftime("%Y-%m-%d")
hoy_partidas = [p for p in st.session_state["partidas"] if p["fecha"] == hoy]
st.write(f"Partidas hoy: {len(hoy_partidas)}")

if hoy_partidas:
    acumulado = {r:{m:0 for m in metricas} for r in roles}
    maximos  = {m:0 for m in metricas}
    # Acumular y calcular máximos
    for p in hoy_partidas:
        for i, rol in enumerate(roles):
            for m in metricas:
                acumulado[rol][m] += p["datos"][i][m]
    for rol in roles:
        for m in metricas:
            prom = acumulado[rol][m] / len(hoy_partidas)
            maximos[m] = max(maximos[m], prom)

    resumen_export = {}
    # Mostrar por rol
    for rol in roles:
        prom = {m: acumulado[rol][m] / len(hoy_partidas) for m in metricas}
        st.subheader(rol)
        buf = generar_grafico(prom, rol, maximos)
        st.image(buf, use_container_width=True)

        # Feedback mejorado
        msg, cal, percentiles = calificar_desempeno(
            [prom[m] for m in metricas], rol, maximos
        )
        st.markdown(f"**Calificación:** {cal}")
        st.markdown(f"**Feedback detallado:**<br>{msg.replace(chr(10), '<br>')}", unsafe_allow_html=True)

        resumen_export[rol] = {
            "Daño %": f"{percentiles['Daño Infligido']:.1f}%",
            "Recibido %": f"{percentiles['Daño Recibido']:.1f}%",
            "Oro %": f"{percentiles['Oro Total']:.1f}%",
            "Part %": f"{percentiles['Participación']:.1f}%",
            "Calificación": cal,
            "Feedback": msg
        }

    # Descarga PDF y Excel
    c1, c2 = st.columns(2)
    with c1:
        pdf_bytes = exportar_pdf(resumen_export, hoy)
        st.download_button("📄 Descargar PDF", data=pdf_bytes,
                           file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
    with c2:
        xlsx = exportar_excel(hoy_partidas)
        st.download_button("📊 Descargar Excel", data=xlsx,
                           file_name=f"Partidas_{hoy}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
