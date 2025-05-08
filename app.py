import streamlit as st
import hashlib
from config import supabase

import mantenimiento_usuarios
# (los demás módulos que cargas abajo)

# --- Funciones de autenticación con Supabase ---

def hash_password(password: str) -> str:
    """SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(usuario: str, contrasena: str) -> str | None:
    """
    Comprueba en Supabase que el usuario exista y la contraseña hashee coincida.
    Devuelve el rol si OK, o None si falla o no hay filas.
    """
    hashed = hash_password(contrasena)
    try:
        resp = (
            supabase
            .table("usuarios")
            .select("usuario, password, rol")
            .eq("usuario", usuario)
            .maybe_single()
            .execute()
        )
    except Exception:
        # Si la consulta lanza cualquier excepción, tratamos como fallo de login
        return None

    # Si resp es None o no viene el atributo data, o data es None → fallo
    if resp is None or not hasattr(resp, "data") or resp.data is None:
        return None

    fila = resp.data
    # Aseguramos que fila sea un dict (y no lista u otro tipo)
    if not isinstance(fila, dict):
        return None

    # Finalmente comparamos el hash
    return fila["rol"] if fila.get("password") == hashed else None

def mostrar_login():
    """Pantalla de login con inputs más cortos y centrados."""
    st.markdown("## 🔐 Inicio de Sesión Produccion Proyecto GTD")
    # Creamos tres columnas; la central tendrá el 50% del ancho
    col1, col2, col3 = st.columns([1,1,2])

    with col1:
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if not usuario or not contrasena:
                st.warning("⚠️ Ingresa usuario y contraseña.")
            else:
                rol = verificar_usuario(usuario.strip(), contrasena)
                if rol:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario.strip()
                    st.session_state["rol"] = rol
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")


# --- Función para cargar secciones ---

def cargar_seccion(nombre):
    if nombre == "Resumen de Producción":
        import resumen_produccion; resumen_produccion.app()
    elif nombre == "Ingreso de Producción":
        import ingreso_produccion; ingreso_produccion.app()
    elif nombre == "Mantenimiento de Actividades":
        import mantenimiento_actividades; mantenimiento_actividades.app()
    elif nombre == "Mantenimiento de Personal":
        import mantenimiento_personal; mantenimiento_personal.app()
    elif nombre == "Mantenimiento de Tramos":
        import mantenimiento_tramos; mantenimiento_tramos.app()
    elif nombre == "Mantenimiento de Usuarios":
        mantenimiento_usuarios.app()
    elif nombre == "Mantenimiento de Empresas":
        import mantenimiento_empresas; mantenimiento_empresas.app()
    elif nombre == "Registro de Gastos":
        import registro_gastos; registro_gastos.app()
    elif nombre == "Creación de Estado de Pago":
        import creacion_estado_pago; creacion_estado_pago.app()


# --- Inicio de la app ---

st.set_page_config(page_title="Producción de Fibra Óptica", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    with st.sidebar:
        st.markdown(f"### 👋 Hola, {st.session_state['usuario'].capitalize()}")
        seccion = st.radio("Navegación", [
            "Resumen de Producción",
            "Ingreso de Producción",
            "Mantenimiento de Actividades",
            "Mantenimiento de Personal",
            "Mantenimiento de Tramos",
            "Mantenimiento de Usuarios",
            "Mantenimiento de Empresas",
            "Registro de Gastos",
            "Creación de Estado de Pago"
        ])
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

    st.title(f"📋 {seccion}")
    cargar_seccion(seccion)
