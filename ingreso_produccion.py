import streamlit as st
import pandas as pd
from datetime import date
from config import supabase

# --- Acceso a datos vía Supabase ---

def leer_actividades():
    resp = supabase.table("actividades").select(
        "descripcion"
    ).order("descripcion").execute()
    return pd.DataFrame(resp.data)


def leer_personal():
    resp = supabase.table("personal").select("nombre").order("nombre").execute()
    return pd.DataFrame(resp.data)


def leer_tramos():
    resp = supabase.table("tramos").select(
        "triot, tramo, inicio, fin, mufa_inicio, mufa_fin"
    ).execute()
    return pd.DataFrame(resp.data)


def leer_produccion():
    resp = supabase.table("produccion").select("*").execute()
    return pd.DataFrame(resp.data)

# --- Operaciones CRUD en Supabase ---

def guardar_produccion(
    fecha: str,
    actividad: str,
    trabajador: str,
    triot: str,
    tramo: str,
    inicio: str,
    fin: str,
    mufa_origen: str,
    mufa_final: str,
    cantidad: float,
    rematado: int
):
    supabase.table("produccion").insert({
        "fecha": fecha,
        "actividad": actividad,
        "trabajador": trabajador,
        "triot": triot,
        "tramo": tramo,
        "inicio": inicio,
        "fin": fin,
        "mufa_origen": mufa_origen,
        "mufa_final": mufa_final,
        "cantidad": cantidad,
        "rematado": rematado
    }).execute()
    st.success("✅ Producción registrada.")


def actualizar_produccion(
    id_prod: int,
    fecha: str,
    actividad: str,
    trabajador: str,
    triot: str,
    tramo: str,
    inicio: str,
    fin: str,
    mufa_origen: str,
    mufa_final: str,
    cantidad: float,
    rematado: int
):
    supabase.table("produccion").update({
        "fecha": fecha,
        "actividad": actividad,
        "trabajador": trabajador,
        "triot": triot,
        "tramo": tramo,
        "inicio": inicio,
        "fin": fin,
        "mufa_origen": mufa_origen,
        "mufa_final": mufa_final,
        "cantidad": cantidad,
        "rematado": rematado
    }).eq("id", id_prod).execute()
    st.success("✏️ Registro actualizado.")

# --- Interfaz de usuario ---
def app():
    st.subheader("📥 Ingreso de Producción")

    # Reset formulario tras submit
    if st.session_state.get('reset_form'):
        for key in ['inicio', 'fin', 'cantidad', 'rematado', 'fecha', 'actividad', 'trabajador', 'triot', 'tramo']:
            st.session_state.pop(key, None)
        st.session_state['reset_form'] = False

    # Carga catálogos
    df_actividades = leer_actividades()
    df_personal = leer_personal()
    df_tramos = leer_tramos()

    # Guards para tablas vacías
    if 'descripcion' not in df_actividades.columns or df_actividades.empty:
        st.warning("⚠️ Primero registra al menos una actividad en 'Mantenimiento de Actividades'.")
        return
    if 'nombre' not in df_personal.columns or df_personal.empty:
        st.warning("⚠️ Primero registra al menos un trabajador en 'Mantenimiento de Personal'.")
        return
    if 'triot' not in df_tramos.columns or df_tramos.empty:
        st.warning("⚠️ Primero registra al menos un tramo en 'Mantenimiento de Tramos'.")
        return

    # Formulario de ingreso
    with st.form("formulario_produccion"):
        fecha = st.date_input("Fecha", value=date.today(), key="fecha")

        actividades = df_actividades["descripcion"].tolist()
        actividad = st.selectbox("Actividad", actividades, key="actividad")

        personal = df_personal["nombre"].tolist()
        trabajador = st.selectbox("Trabajador", personal, key="trabajador")

        triots = df_tramos["triot"].unique().tolist()
        triot = st.selectbox("TRIOT", triots, key="triot")
        tramos = df_tramos[df_tramos["triot"] == triot]["tramo"].tolist()
        tramo = st.selectbox("Tramo", tramos, key="tramo")

        # Valores por defecto según tramo
        sel = df_tramos[(df_tramos["triot"] == triot) & (df_tramos["tramo"] == tramo)]
        inicio_val = sel["inicio"].iloc[0] if not sel.empty else ""
        fin_val = sel["fin"].iloc[0] if not sel.empty else ""
        mufa_o = sel["mufa_inicio"].iloc[0] if not sel.empty else ""
        mufa_f = sel["mufa_fin"].iloc[0] if not sel.empty else ""

        inicio = st.text_input("Inicio (metros)", value=str(inicio_val), key="inicio")
        fin = st.text_input("Fin (metros)", value=str(fin_val), key="fin")
        st.text_input("MUFA Origen", value=str(mufa_o), disabled=True)
        st.text_input("MUFA Final", value=str(mufa_f), disabled=True)

        cantidad = st.number_input("Cantidad realizada", min_value=0.0, step=1.0, key="cantidad")
        rematado = st.slider("% Rematado", 0, 100, key="rematado")

        submitted = st.form_submit_button("Registrar producción")
        if submitted:
            guardar_produccion(
                fecha.isoformat(), actividad, trabajador,
                triot, tramo,
                inicio, fin,
                mufa_o, mufa_f,
                cantidad, rematado
            )
            st.session_state['reset_form'] = True
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("📄 Historial de producción")
    df_historial = leer_produccion()
    st.dataframe(df_historial, use_container_width=True)

    st.markdown("---")
    st.subheader("✏️ Editar registro existente")
    if not df_historial.empty:
        ids = df_historial["id"].tolist()
        selected_id = st.selectbox("Selecciona el ID a editar", ids, key="edit_id")
        registro = df_historial[df_historial["id"] == selected_id].iloc[0]

        with st.form("editar_produccion"):
            fecha_e = st.date_input("Fecha", value=pd.to_datetime(registro["fecha"]).date(), key="edit_fecha")
            actividad_e = st.selectbox("Actividad", actividades, index=actividades.index(registro["actividad"]), key="edit_actividad")
            trabajador_e = st.selectbox("Trabajador", personal, index=personal.index(registro["trabajador"]), key="edit_trabajador")
            triot_e = st.selectbox("TRIOT", triots, index=triots.index(registro["triot"]), key="edit_triot")
            tramo_e = st.selectbox("Tramo", tramos, index=tramos.index(registro["tramo"]), key="edit_tramo")

            inicio_e = st.text_input("Inicio (metros)", value=str(registro["inicio"]), key="edit_inicio")
            fin_e = st.text_input("Fin (metros)", value=str(registro["fin"]), key="edit_fin")
            st.text_input("MUFA Origen", value=registro["mufa_origen"], disabled=True)
            st.text_input("MUFA Final", value=registro["mufa_final"], disabled=True)
            cantidad_e = st.number_input("Cantidad realizada", value=registro["cantidad"], step=1.0, key="edit_cantidad")
            rematado_e = st.slider("% Rematado", 0, 100, value=int(registro["rematado"]), key="edit_rematado")

            editar = st.form_submit_button("Actualizar registro")
            if editar:
                actualizar_produccion(
                    selected_id,
                    fecha_e.isoformat(), actividad_e, trabajador_e,
                    triot_e, tramo_e,
                    inicio_e, fin_e,
                    registro["mufa_origen"], registro["mufa_final"],
                    cantidad_e, rematado_e
                )
                st.experimental_rerun()


if __name__ == "__main__":
    app()
