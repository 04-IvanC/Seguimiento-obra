import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- CONFIGURACIÓN Y LOGO ---
st.set_page_config(page_title="App de Obra y Presupuesto", layout="centered")

if os.path.exists("logo.png"):
    st.image("logo.png", width=200)
else:
    st.info("Logotipo de la empresa")

# --- MENÚ LATERAL (NAVEGACIÓN) ---
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Seleccione el módulo:", ["Seguimiento de Obra", "Seguimiento de Presupuesto"])

# --- FUNCIÓN COMPARTIDA PARA ENVÍO DE EMAIL ---
def enviar_reporte(df_datos, asunto_mail, nombre_archivo):
    try:
        user_mail = st.secrets["email"]["user"]
        pass_mail = st.secrets["email"]["password"]
        profe_mail = st.secrets["email"]["destinatario_profe"]

        # Generar CSV en memoria
        csv_data = df_datos.to_csv(index=False).encode('utf-8')

        msg = MIMEMultipart()
        msg['From'] = user_mail
        msg['To'] = f"{user_mail}, {profe_mail}"
        msg['Subject'] = asunto_mail

        cuerpo = f"Se adjunta el reporte automático generado el {datetime.now().strftime('%d/%m/%Y')}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={nombre_archivo}")
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_mail, pass_mail)
        server.send_message(msg)
        server.quit()
        st.success("✅ ¡Reporte enviado correctamente por email!")
        st.balloons()
    except Exception as e:
        st.error(f"Error al enviar: {e}")

# --- MÓDULO 1: SEGUIMIENTO DE OBRA ---
if opcion == "Seguimiento de Obra":
    st.title("🏗️ Seguimiento de Obra")
    
    trabajador = st.text_input("Trabajador:")
    fecha_obra = st.date_input("Fecha:", datetime.now())
    
    tareas = ["Trazado y marcado...", "Ejecución rozas...", "Tendido de cables...", "Instalación de mecanismos...", "Pruebas técnicas...", "Programación..."]
    tarea_sel = st.selectbox("Tarea seleccionada:", tareas)
    
    estado_sel = st.selectbox("Estado:", ["Avance según porcentaje indicado", "OK, finalizado", "Finalizado con errores", "Corregidos errores"])
    
    porcentaje = "100%"
    if estado_sel == "Avance según porcentaje indicado":
        val = st.slider("% de avance:", 0, 100, 25, 25)
        porcentaje = f"{val}%"
    
    obs_obra = st.text_area("Comentarios de obra:")

    if st.button("🚀 Enviar Reporte de Obra"):
        df_obra = pd.DataFrame([{"Fecha": fecha_obra, "Trabajador": trabajador, "Tarea": tarea_sel, "Estado": estado_sel, "Avance": porcentaje, "Notas": obs_obra}])
        enviar_reporte(df_obra, f"OBRA: {tarea_sel} - {trabajador}", f"Obra_{trabajador}.csv")

# --- MÓDULO 2: SEGUIMIENTO DE PRESUPUESTO ---
elif opcion == "Seguimiento de Presupuesto":
    st.title("💰 Seguimiento de Presupuesto")
    
    trabajador_p = st.text_input("Trabajador responsable:")
    fecha_p = st.date_input("Fecha albarán:", datetime.now())
    num_albaran = st.text_input("Número de Albarán:")
    
    partidas = ["Material Eléctrico", "Mano de Obra", "Maquinaria", "Domótica / Equipos", "Transporte", "Varios"]
    partida_sel = st.selectbox("Partida asociada:", partidas)
    
    gastos = st.number_input("Gastos de esta partida (€):", min_value=0.0, step=0.01)
    obs_p = st.text_area("Comentarios presupuesto:")

    if st.button("📧 Enviar Reporte de Presupuesto"):
        if not num_albaran or not trabajador_p:
            st.warning("Por favor, rellena el Albarán y el Trabajador.")
        else:
            df_pres = pd.DataFrame([{"Fecha": fecha_p, "Albarán": num_albaran, "Trabajador": trabajador_p, "Partida": partida_sel, "Gasto": f"{gastos}€", "Comentarios": obs_p}])
            enviar_reporte(df_pres, f"PRESUPUESTO: Alb.{num_albaran} - {trabajador_p}", f"Presupuesto_{num_albaran}.csv")
