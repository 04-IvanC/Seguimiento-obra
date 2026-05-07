import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.image("logo.png", width=200)
st.title("🏗️ Seguimiento de Obra")

# Campos del formulario
trabajador = st.text_input("Nombre del Trabajador:")
fecha_envio = st.date_input("Fecha:", datetime.now())

# Listas de Tareas y Estados (Las que tú definiste)
tareas = ["Trazado y marcado...", "Ejecución rozas...", "Tendido de cables...", "Pruebas..."] # (Añade todas aquí)
estados = ["Avance 25%", "Avance 50%", "OK Finalizado", "Errores pendientes..."] # (Añade todos aquí)

tarea_sel = st.selectbox("Tarea:", tareas)
estado_sel = st.selectbox("Estado:", estados)

# Lógica de registro
if st.button("Registrar y Enviar Reporte"):
    df = pd.DataFrame([{ "Fecha": fecha_envio, "Trabajador": trabajador, "Tarea": tarea_sel, "Estado": estado_sel }])
    
    # 1. Crear el archivo Excel (CSV para compatibilidad rápida)
    csv = df.to_csv(index=False).encode('utf-8')
    
    # 2. Configuración de Envío de Mail usando los SECRETS
    try:
        msg = MIMEMultipart()
        msg['From'] = st.secrets["email"]["user"]
        msg['To'] = f"{st.secrets['email']['user']}, {st.secrets['email']['destinatario_profe']}"
        msg['Subject'] = f"Reporte Obra - {trabajador} - {fecha_envio}"
        
        cuerpo = f"Se adjunta el reporte de obra realizado por {trabajador}."
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= Reporte_{fecha_envio}.csv")
        msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
        server.send_message(msg)
        server.quit()
        
        st.success("✅ ¡Reporte enviado con éxito al email!")
    except Exception as e:
        st.error(f"Error al enviar: {e}")
