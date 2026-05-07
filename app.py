import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración y Logo
st.image("logo.png", width=200)
st.title("Seguimiento de Obra")

# 1. Campo para el nombre del trabajador
trabajador = st.text_input("Nombre del Trabajador:")

# 2. Campo para la fecha (automática)
fecha_envio = st.date_input("Fecha del informe:", datetime.now())

# 3. Desplegable de Tareas
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
    "Pruebas de continuidad", "Pruebas de aislamiento", "Verificación de tierras",
    "Programación del automatismo", "Pruebas de funcionamiento"
]
tarea_sel = st.selectbox("Seleccione la tarea:", tareas)

# 4. Desplegable de Estado
estados = [
    "Avance de la tarea en torno al 25% aprox.",
    "Avance de la tarea en torno al 50% aprox.",
    "Avance de la tarea en torno al 75% aprox.",
    "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir",
    "Finalizado y corregidos los errores"
]
estado_sel = st.selectbox("Estado de la tarea:", estados)

# Botón para registrar datos
if st.button("Registrar en Excel"):
    # Aquí creamos un pequeño DataFrame (tabla)
    datos = {
        "Fecha": [fecha_envio],
        "Trabajador": [trabajador],
        "Tarea": [tarea_sel],
        "Estado": [estado_sel]
    }
    df = pd.DataFrame(datos)
    
    # Generar Excel para descargar
    st.success("Registro preparado.")
    st.download_button(
        label="Descargar Excel",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='seguimiento_obra.csv',
        mime='text/csv',
    )
