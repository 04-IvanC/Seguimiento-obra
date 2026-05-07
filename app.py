import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- CONFIGURACIÓN DE PÁGINA Y LOGO ---
st.set_page_config(page_title="Gestión de Obra y Presupuesto", layout="centered")

# Intentar cargar el logo
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)
else:
    st.info("Logotipo de la empresa")

# --- MENÚ LATERAL (NAVEGACIÓN) ---
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Seleccione el módulo:", ["Seguimiento de Obra", "Seguimiento de Presupuesto"])

# --- FUNCIÓN COMPARTIDA PARA ENVÍO DE EMAIL ---
def enviar_reporte(df_datos, asunto_mail, nombre_archivo):
    try:
        # Extraer credenciales de los Secrets de Streamlit
        user_mail = st.secrets["email"]["user"]
        pass_mail = st.secrets["email"]["password"]
        profe_mail = st.secrets["email"]["destinatario_profe"]

        # Convertir DataFrame a CSV
        csv_data = df_datos.to_csv(index=False).encode('utf-8')

        # Configurar el mensaje
        msg = MIMEMultipart()
        msg['From'] = user_mail
        msg['To'] = f"{user_mail}, {profe_mail}"
        msg['Subject'] = asunto_mail

        cuerpo = f"Se adjunta el reporte generado automáticamente desde la App móvil.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo CSV
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={nombre_archivo}")
        msg.attach(part)

        # Conexión al servidor SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_mail, pass_mail)
        server.send_message(msg)
        server.quit()
        
        st.success("✅ ¡Reporte enviado con éxito al email!")
        st.balloons()
    except Exception as e:
        st.error(f"Error al enviar el email: {e}")
        st.info("Revisa la configuración de 'Secrets' en Streamlit Cloud.")

# --- MÓDULO 1: SEGUIMIENTO DE OBRA ---
if opcion == "Seguimiento de Obra":
    st.title("🏗️ Seguimiento de Obra")
    st.write("---")
    
    trabajador = st.text_input("Nombre del Trabajador:")
    fecha_obra = st.date_input("Fecha del informe:", datetime.now())
    
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
    tarea_sel = st.selectbox("Seleccione la tarea:", tareas)
    
    estados_lista = [
        "Avance según porcentaje indicado",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ]
    estado_sel = st.selectbox("Estado actual:", estados_lista)
    
    # Lógica dinámica para el slider
    porcentaje_reportado = "100%"
    if estado_sel == "Avance según porcentaje indicado":
        p_val = st.slider("Indique el % de avance:", 0, 100, 25, step=25)
        porcentaje_reportado = f"{p_val}%"
    
    obs_obra = st.text_area("Observaciones de la obra:")

    if st.button("🚀 Guardar y Enviar Reporte de Obra"):
        if not trabajador:
            st.warning("Por favor, introduce el nombre del trabajador.")
        else:
            df_obra = pd.DataFrame([{
                "Fecha": fecha_obra,
                "Trabajador": trabajador,
                "Tarea": tarea_sel,
                "Estado": estado_sel,
                "Avance": porcentaje_reportado,
                "Observaciones": obs_obra
            }])
            enviar_reporte(df_obra, f"OBRA: {tarea_sel} - {trabajador}", f"Reporte_Obra_{trabajador}.csv")

# --- MÓDULO 2: SEGUIMIENTO DE PRESUPUESTO ---
elif opcion == "Seguimiento de Presupuesto":
    st.title("💰 Seguimiento de Presupuesto")
    st.write("---")
    
    trabajador_p = st.text_input("Trabajador responsable:")
    fecha_p = st.date_input("Fecha del albarán:", datetime.now())
    num_albaran = st.text_input("Número de Albarán:")
    
    partidas = ["Material Eléctrico", "Mano de Obra", "Maquinaria", "Domótica / Equipos", "Transporte", "Varios"]
    partida_sel = st.selectbox("Partida asociada:", partidas)
    
    # Campo de descripción de compra
    desc_compra = st.text_input("Descripción de la compra:")
    
    # Campo de gasto manual (sin botones +/-)
    gasto_input = st.text_input("Gastos de esta partida (€):", placeholder="Ej: 150.75")
    
    obs_p = st.text_area("Comentarios adicionales:")

    if st.button("📧 Enviar Reporte de Presupuesto"):
        try:
            # Validar que el gasto sea un número
            gasto_limpio = gasto_input.replace(",", ".")
            gasto_final = float(gasto_limpio)
            
            if not trabajador_p or not num_albaran or not gasto_input:
                st.warning("Por favor, completa los campos obligatorios (Trabajador, Albarán y Gasto).")
            else:
                df_pres = pd.DataFrame([{
                    "Fecha": fecha_p,
                    "Albarán": num_albaran,
                    "Trabajador": trabajador_p,
                    "Partida": partida_sel,
                    "Descripción": desc_compra,
                    "Gasto": f"{gasto_final}€",
                    "Comentarios": obs_p
                }])
                enviar_reporte(df_pres, f"PRESUPUESTO: Alb.{num_albaran} - {trabajador_p}", f"Presupuesto_{num_albaran}.csv")
        
        except ValueError:
            st.error("⚠️ Por favor, introduce un valor numérico válido en el campo de Gastos.")
