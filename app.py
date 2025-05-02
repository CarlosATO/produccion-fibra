import streamlit as st
import sqlite3
import hashlib

# Función para obtener conexión a la base de datos
def get_connection():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# Función para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verificar si el usuario existe
def verificar_usuario(usuario, contrasena):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT contrasena, rol FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and hash_password(contrasena) == resultado[0]:
        return resultado[1]  # Retorna el rol
    return None

# Insertar usuario admin si no existe
def insertar_usuario_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO usuarios (usuario, contrasena, rol)
            VALUES (?, ?, ?)
        """, ("admin", hash_password("admin123"), "admin"))
        conn.commit()
    conn.close()

# Llamar al insertar admin al iniciar
insertar_usuario_admin()

# Configuración de página
st.set_page_config(page_title="Producción de Fibra Óptica", layout="wide")

# Función para interfaz de login
def mostrar_login():
    st.markdown("## 🔐 Inicio de Sesión")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        rol = verificar_usuario(usuario, contrasena)
        if rol:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["rol"] = rol
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# Función para cargar secciones según opción
def cargar_seccion(nombre):
    if nombre == "Ingreso de Producción":
        import ingreso_produccion
        ingreso_produccion.app()
    elif nombre == "Mantenimiento de Actividades":
        import mantenimiento_actividades
        mantenimiento_actividades.app()
    elif nombre == "Mantenimiento de Personal":
        import mantenimiento_personal
        mantenimiento_personal.app()
    elif nombre == "Mantenimiento de Tramos":
        import mantenimiento_tramos
        mantenimiento_tramos.app()
    elif nombre == "Mantenimiento de Usuarios":
        import mantenimiento_usuarios
        mantenimiento_usuarios.app()

# App principal
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    with st.sidebar:
        st.markdown(f"### 👋 Hola, {st.session_state['usuario'].capitalize()}")
        seccion = st.radio("Navegación", [
            "Ingreso de Producción",
            "Mantenimiento de Actividades",
            "Mantenimiento de Personal",
            "Mantenimiento de Tramos",
            "Mantenimiento de Usuarios"
        ])
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

    st.title(f"📋 {seccion}")
    cargar_seccion(seccion)
