import streamlit as st
import re
import pandas as pd
from config import supabase

# --- Validación de RUT chileno ---
def es_rut_valido(rut: str) -> bool:
    rut_clean = rut.replace('.', '').replace('-', '').upper()
    return bool(re.match(r"^\d{7,8}[0-9K]$", rut_clean))

# --- Funciones de acceso a datos en Supabase ---

def listar_empresas():
    resp = (
        supabase.table("empresas")
        .select("nombre")
        .order("nombre")
        .execute()
    )
    return [r["nombre"] for r in resp.data]


def listar_personal():
    """Devuelve lista de dicts con todo el personal."""
    resp = (
        supabase.table("personal")
        .select("id, nombre, rut, cargo, empresa")
        .order("nombre")
        .execute()
    )
    return resp.data or []


def agregar_personal(nombre: str, rut: str, cargo: str, empresa: str):
    supabase.table("personal").insert({
        "nombre": nombre.strip(),
        "rut": rut.upper().strip(),
        "cargo": cargo.strip(),
        "empresa": empresa
    }).execute()
    st.success("✅ Personal registrado.")


def actualizar_personal(id_pers: int, nombre: str, rut: str, cargo: str, empresa: str):
    supabase.table("personal").update({
        "nombre": nombre.strip(),
        "rut": rut.upper().strip(),
        "cargo": cargo.strip(),
        "empresa": empresa
    }).eq("id", id_pers).execute()
    st.success("✏️ Personal actualizado.")


def eliminar_personal(id_pers: int):
    supabase.table("personal").delete().eq("id", id_pers).execute()
    st.success("🗑️ Personal eliminado.")

# --- Interfaz de usuario ---
def app():
    st.subheader("👷 Mantenimiento de Personal")

    # Carga empresas
    empresas = listar_empresas()
    if not empresas:
        st.warning("⚠️ Debes registrar empresas antes de ingresar personal.")
        return

    # Formulario de registro
    with st.expander("➕ Agregar nuevo trabajador"):
        nombre = st.text_input("Nombre", key="new_nombre")
        rut = st.text_input("RUT (ej: 12345678-9)", key="new_rut")
        cargo = st.text_input("Cargo", key="new_cargo")
        empresa_sel = st.selectbox("Empresa", empresas, key="new_empresa")
        if st.button("Registrar", key="btn_reg_agregar"):
            if not nombre or not rut:
                st.warning("⚠️ Nombre y RUT son obligatorios.")
            elif not es_rut_valido(rut):
                st.error("❌ Formato de RUT incorrecto.")
            else:
                agregar_personal(nombre, rut, cargo, empresa_sel)
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("📋 Personal registrado")

    personal = listar_personal()
    for pers in personal:
        id_pers = pers.get("id")
        with st.expander(f"🔧 {pers.get('nombre')} - {pers.get('rut')}"):
            nombre = st.text_input("Nombre", value=pers.get("nombre"), key=f"nom_{id_pers}")
            rut = st.text_input("RUT", value=pers.get("rut"), key=f"rut_{id_pers}")
            cargo = st.text_input("Cargo", value=pers.get("cargo"), key=f"car_{id_pers}")
            empresa_sel = st.selectbox(
                "Empresa",
                empresas,
                index=empresas.index(pers.get("empresa")) if pers.get("empresa") in empresas else 0,
                key=f"emp_{id_pers}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{id_pers}"):
                    if not es_rut_valido(rut):
                        st.error("❌ Formato de RUT incorrecto. No se puede actualizar.")
                    else:
                        actualizar_personal(id_pers, nombre, rut, cargo, empresa_sel)
                        st.experimental_rerun()
            with col2:
                if st.button("Eliminar", key=f"del_{id_pers}"):
                    eliminar_personal(id_pers)
                    st.experimental_rerun()

if __name__ == "__main__":
    app()