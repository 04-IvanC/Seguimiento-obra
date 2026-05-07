import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="App Obra & Presupuesto Pro", layout="centered")

# Estilo CSS para mejorar la experiencia en dispositivos móviles
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    .stTextArea>div>div>textarea { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Carga de Logo corporativo
if os.path.exists("logo.png"):
    st.image("logo.png", width=180)

# --- 2. NAVEGACIÓN LATERAL ---
st.sidebar.title("Menú de Control")
opcion = st.sidebar.radio("Seleccione Módulo:", ["🚧 Seguimiento de Obra", "💰 Gestión de Presupuesto"])

# --- 3. FUNCIÓN DE ENVÍO DE EMAIL (Soporta archivos y fotos) ---
def enviar_email(df_datos, asunto, archivo_nombre, foto_archivo=None):
    try:
        user = st.secrets["email"]["user"]
        pwd = st.secrets["email"]["password"]
        dest = st.secrets["email"]["destinatario_profe"]

        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = f"{user}, {dest}"
        msg['Subject'] = asunto
        
        cuerpo = f"Nuevo reporte generado desde la App móvil.\nFecha y Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar Reporte Excel (CSV)
        csv_bin = df_datos.to_csv(index=False).encode('utf-8')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_bin)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={archivo_nombre}")
        msg.attach(part)

        # Adjuntar Foto (Evidencia multimedia)
        if foto_archivo is not None:
            img_data = foto_archivo.getvalue()
            img_part = MIMEBase('image', 'png')
            img_part.set_payload(img_data)
            encoders.encode_base64(img_part)
            img_part.add_header('Content-Disposition', 'attachment; filename="evidencia_reporte.png"')
            msg.attach(img_part)

        # Conexión Segura con Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
        
        st.success("✅ ¡Reporte enviado con éxito!")
        st.balloons()
    except Exception as e:
        st.error(f"Error crítico al enviar: {e}")

# --- 4. MÓDULO 1: SEGUIMIENTO DE OBRA ---
if "Obra" in opcion:
    st.title("🚧 Seguimiento de Obra")
    st.write("---")
    
    # Diseño en columnas para ahorrar espacio vertical
    col1, col2 = st.columns(2)
    with col1:
        trabajador = st.text_input("Nombre del Trabajador:")
    with col2:
        fecha = st.date_input("Fecha del Reporte:", datetime.now())

    tarea = st.selectbox("Tarea Realizada:", [
        "Trazado y marcado de cajas, tubos y cuadros", 
        "Ejecución rozas en paredes y techos", 
        "Montaje de soportes", 
        "Colocación tubos y conductos", 
        "Tendido de cables", 
        "Identificación y etiquetado", 
        "Conexionado de cables en bornes", 
        "Instalación de mecanismos", 
        "Cuadro eléctrico", 
        "Equipos domóticos", 
        "Pruebas de continuidad/aislamiento",
        "Programación y Verificación"
    ])
    
    estado_obra = st.selectbox("Estado de la tarea:", [
        "Avance según porcentaje indicado",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ])
    
    # --- LÓGICA DINÁMICA DE CAMPOS ---
    fallo_detectado = "N/A (Sin fallos)"
    porcentaje_avance = "100%"

    # Mostrar selector de fallos SOLO si hay errores pendientes
    if estado_obra == "Finalizado, pero con errores pendientes de corregir":
        fallo_detectado = st.selectbox("Tipo de fallo detectado:", [
            "Fallo de continuidad", 
            "Fallo de aislamiento", 
            "Error de conexionado", 
            "Material defectuoso", 
            "Error en esquema/diseño", 
            "Fallo de configuración software"
        ])
    
    # Mostrar slider SOLO si la tarea está en curso
    if estado_obra == "Avance según porcentaje indicado":
        p_val = st.select_slider("Porcentaje de avance:", options=["0%", "25%", "50%", "75%", "100%"])
        porcentaje_avance = p_val

    comentarios_obra = st.text_area("Comentarios y Observaciones:")
    
    # Captura de imagen
    foto_obra = st.camera_input("📸 Evidencia visual del trabajo")

    if st.button("🚀 Enviar Reporte de Obra"):
        if not trabajador:
            st.warning("⚠️ El nombre del trabajador es obligatorio.")
        else:
            df_obra = pd.DataFrame([{
                "Fecha": fecha, 
                "Trabajador": trabajador, 
                "Tarea": tarea, 
                "Estado": estado_obra, 
                "Fallo": fallo_detectado, 
                "Avance": porcentaje_avance, 
                "Comentarios": comentarios_obra
            }])
            enviar_email(df_obra, f"OBRA: {tarea} - {trabajador}", f"Obra_{trabajador}.csv", foto_obra)

# --- 5. MÓDULO 2: GESTIÓN DE PRESUPUESTO ---
else:
    st.title("💰 Seguimiento de Presupuesto")
    st.write("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        albaran = st.text_input("Número de Albarán / Factura:")
    with c2:
        gasto_raw = st.text_input("Gasto Importe (€):", placeholder="0.00")
    
    trabajador_p = st.text_input("Trabajador que registra el gasto:")
    
    partida = st.selectbox("Partida Presupuestaria:", [
        "Material Eléctrico", 
        "Mano de Obra", 
        "Transporte y Logística", 
        "Alquiler de Maquinaria", 
        "Pequeño Material / Varios"
    ])
    
    descripcion_p = st.text_input("Descripción detallada de la compra:")
    comentarios_p = st.text_area("Notas adicionales del presupuesto:")
    
    # Captura de imagen del ticket/albarán
    foto_alb = st.camera_input("📸 Foto del documento (Albarán)")

    if st.button("📧 Registrar y Enviar Gasto"):
        try:
            # Limpieza y validación de número
            gasto_final = float(gasto_raw.replace(",", "."))
            
            if not albaran or not trabajador_p:
                st.warning("⚠️ Albarán y Trabajador son campos obligatorios.")
            else:
                df_pres = pd.DataFrame([{
                    "Fecha": datetime.now().date(),
                    "Albarán": albaran, 
                    "Trabajador": trabajador_p,
                    "Partida": partida, 
                    "Descripción": descripcion_p, 
                    "Gasto": f"{gasto_final}€", 
                    "Comentarios": comentarios_p
                }])
                enviar_email(df_pres, f"PRESUPUESTO: Alb.{albaran} - {trabajador_p}", f"Presupuesto_{albaran}.csv", foto_alb)
        except ValueError:
            st.error("❌ El importe del gasto debe ser un número válido.")
