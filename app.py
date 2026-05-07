import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuración de página y Logo
st.set_page_config(page_title="Seguimiento de Obra", layout="centered")

if os.path.exists("logo.png"):
    st.image("logo.png", width=200)
else:
    st.info("Logotipo de la empresa")

st.title("🏗️ Control de Avance de Obra")
st.write("---")

# Campos de identificación
trabajador = st.text_input("Nombre del Trabajador:")
fecha_reporte = st.date_input("Fecha del informe:", datetime.now())

# 1. Desplegable de Tareas
tareas = [
    "Trazado y marcado de cajas, tubos y cuadros",
    "Ejecución rozas en paredes y techos",
    "Montaje de soportes",
    "Colocación tubos y conductos",
    "Tendido de cables",
    "Identificación y etiquetado",
    "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos",
    "Fijación de carril DIN y mecanismos en cuadro eléctrico",
    "Cableado interno del cuadro eléctrico",
    "Configuración de equipos domóticos y/o automáticos",
    "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
    "Pruebas de continuidad",
    "Pruebas de aislamiento",
    "Verificación de tierras",
    "Programación del automatismo",
    "Pruebas de funcionamiento"
]
tarea_sel = st.selectbox("Seleccione la tarea de la obra:", tareas)

# 2. Desplegable de Estado
estados_lista = [
    "Avance según porcentaje indicado",
    "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir",
    "Finalizado y corregidos los errores"
]
estado_sel = st.selectbox("Estado actual de la tarea:", estados_lista)

# --- LÓGICA DINÁMICA PARA EL SLIDER ---
porcentaje_valor = "N/A" # Valor por defecto si está finalizado

if estado_sel == "Avance según porcentaje indicado":
    porcentaje = st.slider("Indique el % de avance de la tarea:", 0, 100, 25, step=25)
    porcentaje_valor = f"{porcentaje}%"
else:
    # Si está finalizado en cualquiera de sus formas, asumimos 100% o estado final
    porcentaje_valor = "100% (Finalizado)"

observaciones = st.text_area("Comentarios u observaciones adicionales:")

# Botón de envío
if st.button("🚀 Guardar y Enviar Reporte por Email"):
    if not trabajador:
        st.warning("Por favor, introduce tu nombre antes de enviar.")
    else:
        # Preparar datos para el Excel/CSV
        datos = {
            "Fecha": [fecha_reporte],
            "Trabajador": [trabajador],
            "Tarea": [tarea_sel],
            "Estado": [estado_sel],
            "Avance Real": [porcentaje_valor],
            "Observaciones": [observaciones]
        }
        df = pd.DataFrame(datos)
        csv_data = df.to_csv(index=False).encode('utf-8')

        # ENVÍO DE EMAIL (Usando st.secrets)
        try:
            user_mail = st.secrets["email"]["user"]
            pass_mail = st.secrets["email"]["password"]
            profe_mail = st.secrets["email"]["destinatario_profe"]

            msg = MIMEMultipart()
            msg['From'] = user_mail
            msg['To'] = f"{user_mail}, {profe_mail}"
            msg['Subject'] = f"Reporte Obra: {tarea_sel} - {trabajador}"

            cuerpo = f"Informe de seguimiento de obra.\nTrabajador: {trabajador}\nTarea: {tarea_sel}\nEstado: {estado_sel}\nAvance: {porcentaje_valor}"
            msg.attach(MIMEText(cuerpo, 'plain'))

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(csv_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename=Reporte_{trabajador}.csv")
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_mail, pass_mail)
            server.send_message(msg)
            server.quit()

            st.success("✅ ¡Reporte enviado con éxito!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error al enviar: {e}")
