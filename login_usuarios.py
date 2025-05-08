import streamlit as st
import hashlib
from config import supabase

# --- Autenticación vía tabla "usuarios" en Supabase ---
# La tabla "usuarios" debe existir en tu proyecto Supabase
# con columnas: id, nombre, usuario, password (hash), rol

def verificar_credenciales(usuario: str, password: str):
    # Consulta al registro de usuario
    resp = (
        supabase
        .table("usuarios")
        .select("nombre, usuario, password, rol")
        .eq("usuario", usuario)
        .limit(1)
        .execute()
    )
    data = resp.data
    if not data:
        return None
    user = data[0]
    # Comparar hash de la contraseña
    if user["password"] == hashlib.sha256(password.encode()).hexdigest():
        return {"nombre": user["nombre"], "usuario": user["usuario"], "rol": user["rol"]}
    return None

# --- Interfaz de Login en Streamlit ---
if "usuario" not in st.session_state:
    st.title("🔐 Inicio de Sesión")
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Iniciar sesión")
        if login_btn:
            user = verificar_credenciales(usuario, password)
            if user:
                # Guardar en sesión y recargar
                st.session_state.usuario = user["usuario"]
                st.session_state.nombre = user["nombre"]
                st.session_state.rol = user["rol"]
                st.success(f"Bienvenido, {user['nombre']} 👋")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
else:
    # Ya autenticado: mostrar sidebar y contenido protegido
    st.sidebar.success(f"Sesión activa: {st.session_state.nombre}")
    if st.sidebar.button("Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
    st.title("✅ Acceso permitido")
    st.markdown("Aquí irá tu contenido protegido (formulario, reportes, etc.)")
