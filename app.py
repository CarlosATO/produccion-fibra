
import streamlit as st
import sqlite3
import hashlib
import os

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def verificar_credenciales(usuario, password):
    conn = crear_conexion()
    cursor = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()
    conn.close()
    if user and user[3] == hashlib.sha256(password.encode()).hexdigest():
        return {"nombre": user[1], "usuario": user[2], "rol": user[4]}
    return None

def inicializar_usuarios():
    conn = crear_conexion()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            usuario TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    """)
    conn.commit()
    cursor = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
    if cursor.fetchone() is None:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute("INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                     ("Administrador", "admin", admin_pass, "admin"))
        conn.commit()
    conn.close()

inicializar_usuarios()

# --- INICIO DE SESIÓN ---
if "usuario" not in st.session_state:
    st.title("🔐 Inicio de Sesión")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Iniciar sesión"):
            user = verificar_credenciales(usuario, password)
            if user:
                st.session_state.usuario = user["usuario"]
                st.session_state.nombre = user["nombre"]
                st.session_state.rol = user["rol"]
                st.success(f"Bienvenido, {user['nombre']} 👋")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title(f"👋 Hola, {st.session_state.nombre}")
opciones_admin = {
    "📥 Ingreso de Producción": "ingreso_produccion.py",
    "🧱 Mantenimiento de Actividades": "mantenimiento_actividades.py",
    "👷 Mantenimiento de Personal": "mantenimiento_personal.py",
    "📍 Mantenimiento de Tramos": "mantenimiento_tramos.py",
    "👥 Mantenimiento de Usuarios": "mantenimiento_usuarios.py"
}
opciones_otros = {
    "📥 Ingreso de Producción": "ingreso_produccion.py"
}

menu = opciones_admin if st.session_state.rol == "admin" else opciones_otros
seleccion = st.sidebar.radio("Navegación", list(menu.keys()))
st.sidebar.button("Cerrar sesión", on_click=lambda: [st.session_state.clear(), st.rerun()])

# --- CARGA DEL MÓDULO SELECCIONADO ---
st.markdown(f"# {seleccion}")
archivo = menu[seleccion]

if os.path.exists(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        codigo = f.read()
    exec(codigo, globals())
else:
    st.error("⚠️ Módulo no encontrado.")
