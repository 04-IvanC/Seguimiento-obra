import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="App Obra & Presupuesto", layout="centered")

# Estilo visual para botones y campos
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=180)

# --- NAVEGACIÓN ---
st.sidebar.title("Menú de Control")
opcion = st.sidebar.radio("Ir a:", ["🚧 Seguimiento de Obra", "💰 Gestión de Presupuesto"])

# --- FUNCIÓN DE ENVÍO DE EMAIL ---
def enviar_email(df_datos, asunto, archivo_nombre, foto_archivo=None):
    try:
        user = st.secrets["email"]["user"]
        pwd = st.secrets["email"]["password"]
        dest = st.secrets["email"]["destinatario_profe"]

        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = f"{user}, {dest}"
        msg['Subject'] = asunto
        
        cuerpo = f"Nuevo reporte generado.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar Excel (CSV)
        csv_bin = df_datos.to_csv(index=False).encode('utf-8')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_bin)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={archivo_nombre}")
        msg.attach(part)

        # Adjuntar Foto
        if foto_archivo is not None:
            img_data = foto_archivo.getvalue()
            img_part = MIMEBase('image', 'png')
            img_part.set_payload(img_data)
            encoders.encode_base64(img_part)
            img_part.add_header('Content-Disposition', 'attachment; filename="evidencia.png"')
            msg.attach(img_part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
        
        st.success("✅ Reporte enviado con éxito.")
        st.balloons()
    except Exception as e:
        st.error(f"Error al enviar: {e}")

# --- MÓDULO 1: SEGUIMIENTO DE OBRA ---
if "Obra" in opcion:
    st.title("🚧 Seguimiento de Obra")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        trabajador = st.text_input("Trabajador:")
    with col2:
        fecha = st.date_input("Fecha:", datetime.now())

    tarea = st.selectbox("Seleccione la tarea:", [
        "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos", 
        "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables", 
        "Identificación y etiquetado", "Conexionado de cables", "Instalación de mecanismos", 
        "Cuadro eléctrico", "Equipos domóticos", "Pruebas y verificación"
    ])
    
    estado_obra = st.selectbox("Estado actual:", [
        "Avance según porcentaje indicado",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ])
    
    # Lógica para mostrar errores o slider
    fallo_detectado = "Ninguno"
    porcentaje_avance = "100%"

    if "errores" in estado_obra.lower():
        fallo_detectado = st.selectbox("Tipo de fallo detectado:", [
            "Fallo de continuidad", "Fallo de aislamiento", "Error de conexionado", 
            "Material defectuoso", "Error en esquema", "Otro (especificar en comentarios)"
        ])
    
    if estado_obra == "Avance según porcentaje indicado":
        p_val = st.select_slider("Porcentaje de avance:", options=["0%", "25%", "50%", "75%", "100%"])
        porcentaje_avance = p_val

    # Caja de comentarios
    comentarios_obra = st.text_area("Comentarios / Observaciones de la obra:")
    
    foto_obra = st.camera_input("📸 Foto del avance")

    if st.button("🚀 Enviar Reporte de Obra"):
        if not trabajador:
            st.warning("Por favor, introduce el nombre del trabajador.")
        else:
            df_obra = pd.DataFrame([{
                "Fecha": fecha, "Trabajador": trabajador, "Tarea": tarea, 
                "Estado": estado_obra, "Fallo": fallo_detectado, 
                "Avance": porcentaje_avance, "Comentarios": comentarios_obra
            }])
            enviar_email(df_obra, f"OBRA: {tarea} - {trabajador}", f"Obra_{trabajador}.csv", foto_obra)

# --- MÓDULO 2: GESTIÓN DE PRESUPUESTO ---
else:
    st.title("💰 Seguimiento de Presupuesto")
    st.write("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        albaran = st.text_input("Nº de Albarán:")
    with c2:
        gasto_raw = st.text_input("Gasto (€):")
    
    partida = st.selectbox("Partida:", ["Material Eléctrico", "Mano de Obra", "Transporte", "Maquinaria", "Varios"])
    descripcion_p = st.text_input("Descripción de la compra:")
    comentarios_p = st.text_area("Comentarios adicionales presupuesto:")
    
    foto_alb = st.camera_input("📸 Foto del Albarán")

    if st.button("📧 Enviar Reporte de Gasto"):
        try:
            gasto_final = float(gasto_raw.replace(",", "."))
            if not albaran or not gasto_raw:
                st.warning("Completa Albarán y Gasto.")
            else:
                df_pres = pd.DataFrame([{
                    "Albarán": albaran, "Fecha": datetime.now().date(), "Partida": partida, 
                    "Descripción": descripcion_p, "Gasto": f"{gasto_final}€", "Comentarios": comentarios_p
                }])
                enviar_email(df_pres, f"PRESUPUESTO: Alb.{albaran}", f"Presupuesto_{albaran}.csv", foto_alb)
        except ValueError:
            st.error("⚠️ Introduce un número válido en Gasto.")
