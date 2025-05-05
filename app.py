# app.py
import streamlit as st
import matplotlib.pyplot as plt
from math import pi
import io
import base64
from datetime import datetime
from fpdf import FPDF
import pandas as pd

# --- CONFIGURACIÓN Y AUTENTICACIÓN ---
st.set_page_config(page_title="WOLF SEEKERS - Registro", layout="wide")

usuarios_permitidos = {"Tivi": "2107", "Ghost": "203"}
def autenticar_usuario(usuario, clave):
    return usuario in usuarios_permitidos and usuarios_permitidos[usuario] == clave

# --- FUNCIONES DE NEGOCIO ---
def calificar_desempeno(valores_norm, rol, maximos):
    dmg, rec, oro, part = valores_norm[:4]
    percentil_dmg = (dmg / maximos['Daño Infligido']) * 100 if maximos['Daño Infligido'] else 0
    percentil_rec = (rec / maximos['Daño Recibido']) * 100 if maximos['Daño Recibido'] else 0
    percentil_oro = (oro / maximos['Oro Total']) * 100 if maximos['Oro Total'] else 0
    percentil_part = (part / maximos['Participación']) * 100 if maximos['Participación'] else 0

    reglas = {
        "TOPLANER": lambda dmg, oro, part: (dmg >= 80 and oro >= 60 and part >= 60),
        "JUNGLER": lambda dmg, oro, part: (dmg >= 85 and oro >= 70 and part >= 60),
        "MIDLANER": lambda dmg, oro, part: (dmg >= 85 and oro >= 70 and part >= 60),
        "ADCARRY": lambda dmg, oro, part: (dmg >= 90 and oro >= 70 and part >= 60),
        "SUPPORT": lambda dmg, oro, part: (dmg >= 60 and oro >= 50 and part >= 70),
    }

    if reglas[rol](percentil_dmg, percentil_oro, percentil_part):
        return f"Excelente desempeño como {rol}. ¡Sigue así!", "Excelente", percentil_dmg, percentil_rec, percentil_oro, percentil_part
    else:
        return f"Requiere mejorar como {rol}.", "Bajo", percentil_dmg, percentil_rec, percentil_oro, percentil_part

def generar_grafico(datos, titulo, categorias, maximos):
    valores = list(datos.values())
    valores_norm = [v / maximos[c] * 100 if maximos[c] else 0 for v, c in zip(valores, categorias)]

    N = len(categorias)
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    valores_norm += valores_norm[:1]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores_norm, color='#FFD700', linewidth=2)
    ax.fill(angulos, valores_norm, color='#FFD700', alpha=0.3)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, color='white')
    ax.set_yticklabels([])
    ax.set_title(titulo, color='white')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    return buf

def exportar_pdf(datos_por_rol, fecha, equipo="WOLF SEEKERS"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Resumen Diario - {fecha}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Equipo: {equipo}", ln=True, align="C")
    
    for rol, resumen in datos_por_rol.items():
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in resumen.items():
            pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)
    
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def exportar_excel(partidas):
    registros = []
    for p in partidas:
        fecha = p["fecha"]
        for i, rol in enumerate(["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]):
            datos = p["datos"][i]
            datos["Fecha"] = fecha
            datos["Rol"] = rol
            registros.append(datos)
    df = pd.DataFrame(registros)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# --- INTERFAZ ---
st.markdown("<h1 style='color:#FFD700;'>🏆 WOLF SEEKERS E-SPORTS</h1>", unsafe_allow_html=True)

# Login
usuario = st.sidebar.text_input("Usuario")
clave = st.sidebar.text_input("Contraseña", type="password")
if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario, clave):
        st.session_state["autenticado"] = True
        st.sidebar.success("¡Sesión iniciada!")
    else:
        st.sidebar.error("Credenciales incorrectas.")

if st.session_state.get("autenticado"):
    roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]
    if "registro_partidas" not in st.session_state:
        st.session_state["registro_partidas"] = []

    st.subheader("📋 Registro de Partida")
    jugadores = []
    with st.form("registro_form"):
        for i, rol in enumerate(roles):
            st.markdown(f"**{rol}**")
            col1, col2, col3, col4 = st.columns(4)
            dmg = col1.number_input(f"Daño Infligido ({rol})", 0, key=f"dmg_{i}")
            rec = col2.number_input(f"Daño Recibido ({rol})", 0, key=f"rec_{i}")
            oro = col3.number_input(f"Oro Total ({rol})", 0, key=f"oro_{i}")
            part = col4.number_input(f"Participación (%) ({rol})", 0, 100, key=f"part_{i}")
            jugadores.append({"Daño Infligido": dmg, "Daño Recibido": rec, "Oro Total": oro, "Participación": part})
        if st.form_submit_button("Guardar"):
            st.session_state["registro_partidas"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "datos": jugadores
            })
            st.success("Partida guardada correctamente.")

    st.subheader("📊 Resumen Diario")
    hoy = datetime.now().strftime("%Y-%m-%d")
    partidas_hoy = [p for p in st.session_state["registro_partidas"] if p["fecha"] == hoy]

    if partidas_hoy:
        acumulado = {r: {"Daño Infligido": 0, "Daño Recibido": 0, "Oro Total": 0, "Participación": 0} for r in roles}
        maximos = {k: 0 for k in ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]}
        for p in partidas_hoy:
            for i, datos in enumerate(p["datos"]):
                rol = roles[i]
                for k in datos:
                    acumulado[rol][k] += datos[k]
                    if datos[k] > maximos[k]:
                        maximos[k] = datos[k]

        resumen_exportar = {}
        for rol in roles:
            promedio = {k: v / len(partidas_hoy) for k, v in acumulado[rol].items()}
            st.markdown(f"### {rol}")
            grafico = generar_grafico(promedio, rol, list(promedio.keys()), maximos)
            st.image(grafico)
            msg, cal, pdmg, prec, poro, ppart = calificar_desempeno(list(promedio.values()), rol, maximos)
            st.write(f"**Calificación:** {cal}")
            st.write(f"**Feedback:** {msg}")
            resumen_exportar[rol] = {
                "Daño %": f"{pdmg:.1f}%",
                "Recibido %": f"{prec:.1f}%",
                "Oro %": f"{poro:.1f}%",
                "Part %": f"{ppart:.1f}%",
                "Calificación": cal
            }

        colpdf, colexcel = st.columns(2)
        with colpdf:
            pdf = exportar_pdf(resumen_exportar, hoy)
            st.download_button("📄 Descargar PDF", data=pdf, file_name=f"Resumen_{hoy}.pdf", mime="application/pdf")
        with colexcel:
            excel = exportar_excel(partidas_hoy)
            st.download_button("📊 Descargar Excel", data=excel, file_name=f"Partidas_{hoy}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.warning("Por favor, inicia sesión para continuar.")
