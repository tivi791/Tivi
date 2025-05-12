import streamlit as st
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import pandas as pd
import io

# ==============================
# CONFIGURACIÓN Y SESIÓN
# ==============================
st.set_page_config(page_title="WOLF SEEKERS E-SPORTS", layout="wide")
st.title("\U0001F3C6 WOLF SEEKERS E-SPORTS - Registro Diario")

# Datos de autenticación
USUARIOS = {"Tivi": "2107", "Ghost": "203", "usuario3": "clave3"}
roles = ["TOPLANER", "JUNGLER", "MIDLANER", "ADCARRY", "SUPPORT"]

# Verificar si la sesión de partidas existe
if "partidas" not in st.session_state:
    st.session_state.partidas = []

# ==============================
# FUNCIONES
# ==============================
def autenticar_usuario(usuario, clave):
    """Función para autenticar usuario"""
    return USUARIOS.get(usuario) == clave

def calificar_desempeno(valores_norm, rol, maximos):
    """Función para calificar el desempeño"""
    pct = lambda v, m: (v / m) * 100 if m else 0
    names = ["Daño Infligido", "Daño Recibido", "Oro Total", "Participación"]
    percentiles = {n: pct(v, maximos.get(n, 1)) for n, v in zip(names, valores_norm)}

    umbrales = {
        "TOPLANER": {"Daño Infligido":80, "Oro Total":60, "Participación":60},
        "JUNGLER": {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "MIDLANER": {"Daño Infligido":85, "Oro Total":70, "Participación":60},
        "ADCARRY": {"Daño Infligido":90, "Oro Total":70, "Participación":60},
        "SUPPORT": {"Daño Infligido":60, "Oro Total":50, "Participación":70},
    }

    mejoras = []
    for métrica, pct_val in percentiles.items():
        if métrica in umbrales[rol] and pct_val < umbrales[rol][métrica]:
            if métrica == "Daño Infligido":
                mejoras.append("Aumenta tu daño infligido: mejora tu farmeo y presiona más en línea.")
            if métrica == "Oro Total":
                mejoras.append("Optimiza tu farmeo de minions y objetivos para mejorar tu oro.")
            if métrica == "Participación":
                mejoras.append("Participa más en peleas de equipo y visión del mapa.")

    if not mejoras:
        mensaje = f"Excelente desempeño como {rol}. Sigue manteniendo tu nivel alto en todas las métricas."
        cal = "Excelente"
    else:
        mensaje = f"Áreas de mejora como {rol}:\n- " + "\n- ".join(mejoras)
        cal = "Bajo"

    return mensaje, cal, percentiles

def generar_grafico(datos, titulo, maximos):
    """Generar gráfico radar"""
    categorias = list(datos.keys())
    valores = [datos[c] for c in categorias]
    valores_norm = [(v / maximos.get(c, 1)) * 100 for v, c in zip(valores, categorias)]  # Se asegura que 'maximos' tenga un valor por defecto
    valores_norm += valores_norm[:1]  # Se agrega el primer valor al final para cerrar el gráfico
    ang = [n/float(len(categorias))*2*pi for n in range(len(categorias))]
    ang += ang[:1]  # Añadimos el primer ángulo para cerrar el gráfico

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(ang, valores_norm, color='#FFD700', linewidth=2)
    ax.fill(ang, valores_norm, color='#FFD700', alpha=0.3)
    ax.set_xticks(ang[:-1])  # Excluimos el último ángulo repetido
    ax.set_xticklabels(categorias, color='white', fontsize=12)
    ax.set_yticklabels([])  # No mostrar las etiquetas del eje Y
    ax.set_title(titulo, color='white')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    plt.close(fig)
    return buf

def exportar_pdf(resumen, fecha, equipo="WOLF SEEKERS E-SPORTS"):
    """Generar PDF de resumen diario"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Resumen Diario - {fecha}", ln=True, align="C")
    pdf.cell(0, 10, f"Equipo: {equipo}", ln=True, align="C")
    for rol, datos in resumen.items():
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, rol, ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in datos.items():
            texto = f"{k}: {v}"
            texto = texto.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 6, texto)
    return pdf.output(dest='S').encode('latin-1')

# ==============================
# INICIO DE SESIÓN
# ==============================
st.sidebar.header("Inicio de sesión")

usuario = st.sidebar.text_input("Usuario")
clave = st.sidebar.text_input("Clave", type="password")

if st.sidebar.button("Iniciar sesión"):
    if autenticar_usuario(usuario, clave):
        st.session_state.usuario = usuario
        st.success("¡Bienvenido, " + usuario + "!")  
    else:
        st.error("Usuario o clave incorrectos")

# Si no está autenticado, no se puede registrar una partida ni ver el resumen
if "usuario" in st.session_state:
    # ==============================
    # REGISTRO PARTIDA
    # ==============================
    st.header("Registrar Nueva Partida")
    nueva_partida = {}

    for rol in roles:
        st.subheader(rol)
        dano = st.number_input(f"Daño Infligido ({rol})", min_value=0)
        recibido = st.number_input(f"Daño Recibido ({rol})", min_value=0)
        oro = st.number_input(f"Oro Total ({rol})", min_value=0)
        participacion = st.number_input(f"Participación ({rol})", min_value=0)
        nueva_partida[rol] = {"dano": dano, "recibido": recibido, "oro": oro, "participacion": participacion}

    # Lista de opciones para comentarios
    st.subheader("Retroalimentación del equipo")
    opciones_comentario = ["Seleccionar una opción...", "AFK", "Problemas de comunicación", "Falta de visión", "Mal ambiente", "Buen trabajo en equipo"]
    comentario = st.selectbox("Seleccione un comentario:", opciones_comentario)

    if st.button("Guardar Partida"):
        st.session_state.partidas.append({"fecha": datetime.date.today(), "datos": nueva_partida, "comentario": comentario})
        st.success("Partida guardada ✔️")

    # ==============================
    # RESUMEN DIARIO
    # ==============================
    st.header("Resumen Diario")
    hoy = datetime.date.today()
    hoy_partidas = [p for p in st.session_state.partidas if p["fecha"] == hoy]
    st.write(f"Partidas hoy: {len(hoy_partidas)}")

    if hoy_partidas:
        acumulado = defaultdict(lambda: {"dano": 0, "recibido": 0, "oro": 0, "participacion": 0})

        for partida in hoy_partidas:
            for rol in roles:
                datos = partida["datos"][rol]
                acumulado[rol]["dano"] += datos["dano"]
                acumulado[rol]["recibido"] += datos["recibido"]
                acumulado[rol]["oro"] += datos["oro"]
                acumulado[rol]["participacion"] += datos["participacion"]

        resumen = {}
        for rol in roles:
            stats = acumulado[rol]
            # No dividir por el número de partidas, acumulamos los valores
            promedio = {k: stats[k] for k in stats}
            maximos = {"Daño Infligido":200000, "Daño Recibido":200000, "Oro Total":20000, "Participación":100}
            valores_norm = [promedio["dano"], promedio["recibido"], promedio["oro"], promedio["participacion"]]
            feedback, calif, percentiles = calificar_desempeno(valores_norm, rol, maximos)
            resumen[rol] = {
                "Promedio Daño Infligido": promedio["dano"],
                "Promedio Daño Recibido": promedio["recibido"],
                "Promedio Oro Total": promedio["oro"],
                "Promedio Participación": promedio["participacion"],
                "Calificación": calif,
                "Feedback": feedback
            }
            buf = generar_grafico(percentiles, rol, maximos)
            st.image(buf)

        # Mostrar resumen
        for rol, datos in resumen.items():
            st.subheader(rol)
            for k, v in datos.items():
                st.write(f"{k}: {v}")

        # ==============================
        # EXPORTAR PDF
        # ==============================
        if st.button("Exportar PDF"):
            pdf_output = exportar_pdf(resumen, hoy)
            st.download_button("Descargar PDF", pdf_output, file_name=f"resumen_{hoy}.pdf")
