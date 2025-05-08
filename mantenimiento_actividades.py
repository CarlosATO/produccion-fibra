import streamlit as st
from config import supabase

# --- Acceso y operaciones sobre la tabla "actividades" en Supabase ---

def listar_actividades():
    """Devuelve lista de dicts con todas las actividades ordenadas por descripción."""
    resp = (
        supabase
        .table("actividades")
        .select("id, codigo, descripcion, unidad, grupo, tipo, valor_produccion, valor_venta")
        .order("descripcion")
        .execute()
    )
    return resp.data or []


def agregar_actividad(codigo: str,
                     descripcion: str,
                     unidad: str,
                     grupo: str,
                     tipo: str,
                     valor_prod: float,
                     valor_venta: float):
    supabase.table("actividades").insert({
        "codigo": codigo,
        "descripcion": descripcion,
        "unidad": unidad,
        "grupo": grupo,
        "tipo": tipo,
        "valor_produccion": valor_prod,
        "valor_venta": valor_venta
    }).execute()
    st.success("✅ Actividad registrada.")
    # Recarga la app
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st, 'rerun'):
        st.rerun()


def actualizar_actividad(id_act: int,
                         codigo: str,
                         descripcion: str,
                         unidad: str,
                         grupo: str,
                         tipo: str,
                         valor_prod: float,
                         valor_venta: float):
    supabase.table("actividades").update({
        "codigo": codigo,
        "descripcion": descripcion,
        "unidad": unidad,
        "grupo": grupo,
        "tipo": tipo,
        "valor_produccion": valor_prod,
        "valor_venta": valor_venta
    }).eq("id", id_act).execute()
    st.success("✏️ Actividad actualizada.")
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st, 'rerun'):
        st.rerun()


def eliminar_actividad(id_act: int):
    supabase.table("actividades").delete().eq("id", id_act).execute()
    st.success("🗑️ Actividad eliminada.")
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st, 'rerun'):
        st.rerun()

# --- Interfaz de usuario ---

def app():
    st.subheader("🧱 Mantenimiento de Actividades")

    # 1) Formulario de alta
    with st.expander("➕ Agregar nueva actividad"):
        codigo = st.text_input("Código", key="new_codigo")
        descripcion = st.text_area("Descripción", key="new_descripcion")
        unidad = st.text_input("Unidad", key="new_unidad")
        grupo = st.text_input("Grupo", key="new_grupo")
        tipo = st.selectbox("Tipo", ["Programada", "Extra Programática"], key="new_tipo")
        valor_prod = st.number_input(
            "Valor Producción",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="new_valor_prod"
        )
        valor_venta = st.number_input(
            "Valor Venta",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="new_valor_venta"
        )
        if st.button("Registrar", key="btn_agregar_act"):
            if codigo and descripcion:
                agregar_actividad(codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta)
            else:
                st.warning("⚠️ Completa al menos código y descripción.")

    st.markdown("---")
    st.subheader("📄 Actividades registradas")
    actividades = listar_actividades()

    for act in actividades:
        act_id = act.get("id")
        with st.expander(f"🔧 {act.get('codigo')} - {act.get('descripcion')}", expanded=False):
            codigo = st.text_input("Código", value=act.get("codigo"), key=f"cod_{act_id}")
            descripcion = st.text_area("Descripción", value=act.get("descripcion"), key=f"desc_{act_id}")
            unidad = st.text_input("Unidad", value=act.get("unidad"), key=f"uni_{act_id}")
            grupo = st.text_input("Grupo", value=act.get("grupo"), key=f"gru_{act_id}")
            tipo_val = act.get("tipo") or "Programada"
            tipo = st.selectbox(
                "Tipo",
                ["Programada", "Extra Programática"],
                index=0 if tipo_val == "Programada" else 1,
                key=f"tipo_{act_id}"
            )
            # Asegurar tipos float
            default_prod = float(act.get("valor_produccion", 0.0))
            default_venta = float(act.get("valor_venta", 0.0))
            valor_prod = st.number_input(
                "Valor Producción",
                min_value=0.0,
                value=default_prod,
                step=100.0,
                key=f"vp_{act_id}"
            )
            valor_venta = st.number_input(
                "Valor Venta",
                min_value=0.0,
                value=default_venta,
                step=100.0,
                key=f"vv_{act_id}"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{act_id}"):
                    actualizar_actividad(act_id, codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta)
            with col2:
                if st.button("Eliminar", key=f"del_{act_id}"):
                    eliminar_actividad(act_id)

if __name__ == "__main__":
    app()
