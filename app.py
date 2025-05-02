
import streamlit as st
import sqlite3
import hashlib

# Función para crear usuario admin si no existe
def crear_usuario_admin_si_no_existe():
    conn = sqlite3.connect("productividad_fibra.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            contrasena TEXT,
            rol TEXT
        )
    """)
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if cursor.fetchone() is None:
        password_encriptada = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", ("admin", password_encriptada, "admin"))
        conn.commit()
        print("✅ Usuario admin creado automáticamente.")
    conn.close()

crear_usuario_admin_si_no_existe()

# Aquí continuaría el resto del código original de la app
st.set_page_config(page_title="Gestión Producción", layout="wide")

st.title("Aplicación de Producción de Fibra Óptica")
st.markdown("🔐 Esta es una estructura base del archivo `app.py` con verificación de usuario.")
