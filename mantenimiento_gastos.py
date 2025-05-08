import streamlit as st
import pandas as pd
from datetime import date
from config import supabase

# --- Funciones de acceso a datos en Supabase ---

def listar_empresas():
    """Obtiene la lista de nombres de empresas (subcontratos)"""
    resp = supabase.table("empresas").select("nombre").order("nombre").execute()
    return [r["nombre"] for r in resp.data]


def listar_gastos():
    """Devuelve lista de dicts con todos los gastos ordenados por fecha desc"""
    resp = supabase.table("gastos").select(
        "id, empresa, detalle, monto, observacion, fecha"
    ).order("fecha", desc=True).execute()
    return resp.data or []


def agregar_gasto(empresa: str, detalle: str, monto: float, observacion: str):
    """Inserta un nuevo gasto en Supabase"""
    supabase.table("gastos").insert({
        "empresa": empresa,
        "detalle": detalle.title(),
        "monto": monto,
        "observacion": observacion.title(),
        "fecha": date.today().isoformat()
    }).execute()
    st.success("✅ Gasto registrado correctamente.")
    st.experimental_rerun()


def eliminar_gasto(id_gasto: int):
    """Elimina un gasto por ID"""
    supabase.table("gastos").delete().eq("id", id_gasto).execute()
    st.success("🗑️ Gasto eliminado.")
    st.experimental_rerun()

# --- Interfaz de usuario ---
def app():
    st.subheader("💸 Registro de Gastos por Empresa")

    empresas = listar_empresas()
    if not empresas:
        st.warning("⚠️ Debes registrar empresas antes de ingresar gastos.")
        return

    with st.form("form_gasto"):
        empresa = st.selectbox("Nombre del Subcontrato", empresas, key="empresa_gasto")
        detalle = st.text_input("Detalle del gasto", key="detalle_gasto").strip()
        monto = st.number_input("Monto del gasto", min_value=0.0, step=100.0, key="monto_gasto")
        observacion = st.text_area("Observación", key="obs_gasto").strip()
        if st.form_submit_button("Registrar Gasto", key="btn_registrar_gasto"):
            if not detalle:
                st.warning("⚠️ El campo 'Detalle del gasto' es obligatorio.")
            elif monto <= 0:
                st.warning("⚠️ El monto debe ser mayor que 0.")
            else:
                agregar_gasto(empresa, detalle, monto, observacion)

    st.divider()
    st.subheader("📋 Gastos Registrados")

    gastos = listar_gastos()
    if gastos:
        for g in gastos:
            with st.expander(f"{g['empresa']} - {g['detalle']} - ${g['monto']:.0f}"):
                st.write(f"**Fecha:** {g['fecha']}")
                st.write(f"**Observación:** {g['observacion']}")
                if st.button("Eliminar", key=f"del_{g['id']}"):
                    eliminar_gasto(g['id'])
    else:
        st.info("No hay gastos registrados.")

if __name__ == '__main__':
    app()
