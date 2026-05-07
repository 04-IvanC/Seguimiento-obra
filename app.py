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

# CSS para mejorar la apariencia en móviles
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Logo
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
        
        cuerpo = f"Nuevo reporte generado desde la App.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar Excel (CSV)
        csv_bin = df_datos.to_csv(index=False).encode('utf-8')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_bin)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={archivo_nombre}")
        msg.attach(part)

        # Adjuntar Foto si se tomó una
        if foto_archivo is not None:
            img_data = foto_archivo.getvalue()
            img_part = MIMEBase('image', 'png')
            img_part.set_payload(img_data)
            encoders.encode_base64(img_part)
            img_part.add_header('Content-Disposition', 'attachment; filename="evidencia.png"')
            msg.attach(img_part)

        # Enviar
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
        
        st.success("✅ ¡Reporte y foto enviados con éxito!")
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
        "Trazado y marcado", "Ejecución rozas", "Montaje soportes", 
        "Tendido cables", "Conexionado cuadros", "Pruebas técnicas"
    ])
    
    estado = st.select_slider("Grado de avance:", options=["0%", "25%", "50%", "75%", "100% (Finalizado)"])
    
    # Cámara
    foto_obra = st.camera_input("📸 Evidencia de la tarea")

    if st.button("🚀 Enviar Reporte de Obra"):
        if not trabajador:
            st.warning("Por favor, introduce tu nombre.")
        else:
            df_obra = pd.DataFrame([{
                "Fecha": fecha, "Trabajador": trabajador, "Tarea": tarea, "Estado": estado
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
        gasto_raw = st.text_input("Gasto (€):", placeholder="0.00")
    
    partida = st.selectbox("Partida:", ["Material Eléctrico", "Mano de Obra", "Transporte", "Otros"])
    descripcion = st.text_input("Descripción de la compra:")
    
    # Cámara
    foto_alb = st.camera_input("📸 Foto del Albarán")

    if st.button("📧 Enviar Reporte de Gasto"):
        try:
            gasto_final = float(gasto_raw.replace(",", "."))
            if not albaran or not gasto_raw:
                st.warning("Campos obligatorios: Albarán y Gasto.")
            else:
                df_pres = pd.DataFrame([{
                    "Albarán": albaran, "Fecha": datetime.now().date(), "Partida": partida, 
                    "Descripción": descripcion, "Gasto": f"{gasto_final}€"
                }])
                enviar_email(df_pres, f"PRESUPUESTO: Alb.{albaran}", f"Presupuesto_{albaran}.csv", foto_alb)
        except ValueError:
            st.error("⚠️ Introduce un número válido en el campo Gasto.")
