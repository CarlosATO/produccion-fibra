
import streamlit as st
import sqlite3
import hashlib

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

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

    # Crear usuario admin si no existe
    cursor = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
    if cursor.fetchone() is None:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute("INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                     ("Administrador", "admin", password_hash, "admin"))
        conn.commit()
    conn.close()

def verificar_credenciales(usuario, password):
    conn = crear_conexion()
    cursor = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()
    conn.close()
    if user and user[3] == hashlib.sha256(password.encode()).hexdigest():
        return {"nombre": user[1], "usuario": user[2], "rol": user[4]}
    return None

# Inicializar base de datos
inicializar_usuarios()

# Interfaz de login
if "usuario" not in st.session_state:
    st.title("🔐 Inicio de Sesión")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Iniciar sesión")

        if login_btn:
            user = verificar_credenciales(usuario, password)
            if user:
                st.session_state.usuario = user["usuario"]
                st.session_state.nombre = user["nombre"]
                st.session_state.rol = user["rol"]
                st.success(f"Bienvenido, {user['nombre']} 👋")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

else:
    st.sidebar.success(f"Sesión activa: {st.session_state.nombre}")
    if st.sidebar.button("Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

    st.title("✅ Acceso permitido")
    st.markdown("Aquí irá tu contenido protegido (formulario, reportes, etc.)")
