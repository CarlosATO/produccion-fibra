import streamlit as st
import hashlib
from config import supabase

# --- Funciones de acceso a datos en Supabase ---

def listar_usuarios():
    """Devuelve lista de dicts con id, nombre, usuario y rol."""
    resp = (
        supabase
        .table("usuarios")
        .select("id, nombre, usuario, rol")
        .order("usuario")
        .execute()
    )
    return resp.data or []

def encriptar_contrasena(contrasena: str) -> str:
    """Hash SHA-256 de contraseña"""
    return hashlib.sha256(contrasena.encode()).hexdigest()

def agregar_usuario(nombre: str, usuario: str, contrasena: str, rol: str):
    """Inserta un nuevo usuario."""
    try:
        supabase.table("usuarios").insert({
            "nombre": nombre.strip(),
            "usuario": usuario.strip(),
            "password": encriptar_contrasena(contrasena),
            "rol": rol
        }).execute()
        st.success("✅ Usuario agregado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al agregar usuario: {e}")

def actualizar_usuario(id_usuario: int, nuevo_usuario: str, nueva_contrasena: str, nuevo_rol: str):
    """Actualiza usuario y/o contraseña y rol."""
    datos = {"usuario": nuevo_usuario.strip(), "rol": nuevo_rol}
    if nueva_contrasena:
        datos["password"] = encriptar_contrasena(nueva_contrasena)
    supabase.table("usuarios").update(datos).eq("id", id_usuario).execute()
    st.success("✅ Usuario actualizado.")

def eliminar_usuario(id_usuario: int):
    """Elimina usuario por ID."""
    supabase.table("usuarios").delete().eq("id", id_usuario).execute()
    st.success("🗑️ Usuario eliminado.")


# --- Interfaz de usuario ---

def app():
    st.subheader("🔐 Mantenimiento de Usuarios")

    # 1) Agregar nuevo usuario
    with st.expander("➕ Agregar nuevo usuario"):
        nombre = st.text_input("Nombre completo", key="new_nombre")
        usuario = st.text_input("Usuario", key="new_usuario")
        contrasena = st.text_input("Contraseña", type="password", key="new_password")
        rol = st.selectbox("Rol", ["admin", "editor", "visualizador"], key="new_rol")
        if st.button("Agregar usuario", key="btn_agregar_usuario"):
            if not (nombre and usuario and contrasena):
                st.warning("⚠️ Completa nombre, usuario y contraseña.")
            else:
                agregar_usuario(nombre, usuario, contrasena, rol)
                st.rerun()

    st.markdown("---")
    st.subheader("👥 Usuarios registrados")

    usuarios = listar_usuarios()
    for u in usuarios:
        uid = u.get("id")
        with st.expander(f"{u.get('usuario')} ({u.get('rol')})"):
            nombre = st.text_input("Nombre completo",
                                   value=u.get("nombre"),
                                   key=f"nom_{uid}")
            usuario = st.text_input("Usuario",
                                    value=u.get("usuario"),
                                    key=f"usr_{uid}")
            nueva_contrasena = st.text_input("Nueva contraseña (opcional)",
                                             type="password",
                                             key=f"pwd_{uid}")
            rol = st.selectbox(
                "Rol",
                ["admin", "editor", "visualizador"],
                index=["admin", "editor", "visualizador"].index(u.get("rol")),
                key=f"rol_{uid}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{uid}"):
                    actualizar_usuario(uid, usuario, nueva_contrasena, rol)
                    st.rerun()
            with col2:
                if st.button("Eliminar", key=f"del_{uid}"):
                    eliminar_usuario(uid)
                    st.rerun()

if __name__ == "__main__":
    app()
