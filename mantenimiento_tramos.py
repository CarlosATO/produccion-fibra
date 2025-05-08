import streamlit as st
from config import supabase

# --- Funciones de acceso a datos en Supabase ---

def listar_tramos():
    """Devuelve lista de dicts con todos los tramos ordenados por triot y tramo."""
    resp = (
        supabase.table("tramos")
        .select("id, triot, tramo, inicio, fin, mufa_inicio, mufa_fin")
        .order("triot")
        .order("tramo")
        .execute()
    )
    return resp.data or []


def agregar_tramo(triot: str, tramo: str, inicio: str, fin: str, mufa_inicio: str, mufa_fin: str):
    """Inserta un nuevo tramo en Supabase."""
    supabase.table("tramos").insert({
        "triot": triot,
        "tramo": tramo,
        "inicio": inicio,
        "fin": fin,
        "mufa_inicio": mufa_inicio,
        "mufa_fin": mufa_fin
    }).execute()
    st.success("✅ Tramo registrado correctamente.")


def actualizar_tramo(idt: int, triot: str, tramo: str, inicio: str, fin: str, mufa_inicio: str, mufa_fin: str):
    """Actualiza un tramo existente."""
    supabase.table("tramos").update({
        "triot": triot,
        "tramo": tramo,
        "inicio": inicio,
        "fin": fin,
        "mufa_inicio": mufa_inicio,
        "mufa_fin": mufa_fin
    }).eq("id", idt).execute()
    st.success("✏️ Tramo actualizado.")


def eliminar_tramo(idt: int):
    """Elimina un tramo."""
    supabase.table("tramos").delete().eq("id", idt).execute()
    st.success("🗑️ Tramo eliminado.")

# --- Interfaz de usuario ---

def app():
    st.subheader("📍 Mantenimiento de Tramos")

    # 1) Agregar nuevo tramo
    with st.expander("➕ Agregar nuevo tramo"):
        triot = st.text_input("Nombre del TRIOT", key="new_triot")
        tramo = st.text_input("Tramo", key="new_tramo")
        inicio = st.text_input("Inicio (metro)", key="new_inicio")
        fin = st.text_input("Fin (metro)", key="new_fin")
        mufa_inicio = st.text_input("MUFA Inicio", key="new_mufa_inicio")
        mufa_fin = st.text_input("MUFA Fin", key="new_mufa_fin")
        if st.button("Registrar tramo", key="btn_agregar_tramo"):
            if triot and tramo:
                agregar_tramo(triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
            else:
                st.warning("⚠️ Ingresa al menos TRIOT y Tramo.")

    st.markdown("---")
    st.subheader("📄 Tramos registrados")

    tramos = listar_tramos()
    for t in tramos:
        tid = t.get("id")
        with st.expander(f"🔧 {t.get('triot')} - Tramo {t.get('tramo')}"):
            triot = st.text_input("TRIOT", value=t.get("triot"), key=f"tr_{tid}")
            tramo = st.text_input("Tramo", value=t.get("tramo"), key=f"tt_{tid}")
            inicio = st.text_input("Inicio", value=t.get("inicio"), key=f"i_{tid}")
            fin = st.text_input("Fin", value=t.get("fin"), key=f"f_{tid}")
            mufa_inicio = st.text_input("MUFA Inicio", value=t.get("mufa_inicio"), key=f"mi_{tid}")
            mufa_fin = st.text_input("MUFA Fin", value=t.get("mufa_fin"), key=f"mf_{tid}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{tid}"):
                    actualizar_tramo(tid, triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
            with col2:
                if st.button("Eliminar", key=f"del_{tid}"):
                    eliminar_tramo(tid)

if __name__ == "__main__":
    app()
