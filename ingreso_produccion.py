import streamlit as st
import pandas as pd
from datetime import date
from config import supabase

# --- Acceso a datos vía Supabase ---
def leer_actividades():
    resp = supabase.table("actividades").select("descripcion").order("descripcion").execute()
    return pd.DataFrame(resp.data)

def leer_personal():
    resp = supabase.table("personal").select("nombre").order("nombre").execute()
    return pd.DataFrame(resp.data)

def leer_tramos():
    resp = supabase.table("tramos").select(
        "triot, tramo, inicio, fin, mufa_inicio, mufa_fin"
    ).order("triot, tramo").execute()
    return pd.DataFrame(resp.data)

def leer_produccion():
    resp = supabase.table("produccion").select("*").execute()
    return pd.DataFrame(resp.data)

# --- Operaciones CRUD en Supabase ---
def guardar_produccion(**kwargs):
    supabase.table("produccion").insert(kwargs).execute()
    st.success("✅ Producción registrada.")
    _rerun()

def actualizar_produccion(id_prod: int, **kwargs):
    supabase.table("produccion").update(kwargs).eq("id", id_prod).execute()
    st.success("✏️ Registro actualizado.")
    _rerun()

def _rerun():
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st, 'rerun'):
        st.rerun()

# --- Interfaz de usuario ---
def app():
    st.subheader("📥 Ingreso de Producción")

    # Reset formulario tras submit
    if st.session_state.get('reset_form'):
        for k in ['inicio','fin','cantidad','rematado','fecha','actividad',
                  'trabajador','triot','tramo']:
            st.session_state.pop(k, None)
        st.session_state['reset_form'] = False

    # Carga catálogos
    df_act = leer_actividades()
    df_pers = leer_personal()
    df_tr  = leer_tramos()

    # Guards
    if df_act.empty:
        st.warning("⚠️ Primero registra al menos una actividad.")
        return
    if df_pers.empty:
        st.warning("⚠️ Primero registra al menos un trabajador.")
        return
    if df_tr.empty:
        st.warning("⚠️ Primero registra al menos un tramo.")
        return

    with st.form("form_produccion"):
        fecha = st.date_input("Fecha", value=date.today(), key="fecha")

        # SOLO selectbox: teclea para filtrar
        actividad = st.selectbox("Actividad", df_act["descripcion"].tolist(), key="actividad")
        trabajador = st.selectbox("Trabajador", df_pers["nombre"].tolist(), key="trabajador")

        triots = df_tr["triot"].unique().tolist()
        triot = st.selectbox("TRIOT", triots, key="triot")

        # Autocompletar Tramo/Mufa
        df_tri = df_tr[df_tr["triot"] == triot]
        tramo = st.selectbox("Tramo", df_tri["tramo"].tolist(), key="tramo")
        fila = df_tri[df_tri["tramo"] == tramo].iloc[0]
        inicio_val, fin_val = fila["inicio"], fila["fin"]
        mufa_o, mufa_f = fila["mufa_inicio"], fila["mufa_fin"]

        inicio = st.text_input("Inicio (metros)", value=str(inicio_val), key="inicio")
        fin    = st.text_input("Fin (metros)"  , value=str(fin_val)  , key="fin")
        st.text_input("MUFA Origen", value=str(mufa_o), disabled=True)
        st.text_input("MUFA Final" , value=str(mufa_f), disabled=True)

        cantidad = st.number_input("Cantidad realizada", min_value=0.0, value=0.0, step=1.0, key="cantidad")
        rematado = st.slider("% Rematado", 0, 100, key="rematado")

        if st.form_submit_button("Registrar producción"):
            guardar_produccion(
                fecha=fecha.isoformat(),
                actividad=actividad,
                trabajador=trabajador,
                triot=triot,
                tramo=tramo,
                inicio=inicio,
                fin=fin,
                mufa_origen=mufa_o,
                mufa_final=mufa_f,
                cantidad=float(cantidad),
                rematado=int(rematado)
            )
            st.session_state['reset_form'] = True

    st.markdown("---")
    st.subheader("📄 Historial de producción")
    df_hist = leer_produccion()
    st.dataframe(df_hist, use_container_width=True)

    # Editar registro existente
    st.markdown("---")
    st.subheader("✏️ Editar registro existente")
    if not df_hist.empty:
        ids = df_hist["id"].tolist()
        sel_id = st.selectbox("ID a editar", ids, key="edit_id")
        record = df_hist[df_hist["id"] == sel_id].iloc[0]

        with st.form("form_edit"):
            fecha_e = st.date_input("Fecha", value=pd.to_datetime(record["fecha"]).date(), key="edit_fecha")

            # Teclable selectboxes
            act_list = df_act["descripcion"].tolist()
            actividad_e = st.selectbox("Actividad", act_list,
                                       index=act_list.index(record["actividad"]), key="edit_act")

            pers_list = df_pers["nombre"].tolist()
            trabajador_e = st.selectbox("Trabajador", pers_list,
                                        index=pers_list.index(record["trabajador"]), key="edit_pers")

            triots = df_tr["triot"].unique().tolist()
            triot_e = st.selectbox("TRIOT", triots,
                                   index=triots.index(record["triot"]), key="edit_triot")

            df_tri2 = df_tr[df_tr["triot"] == triot_e]
            tramo_e = st.selectbox("Tramo", df_tri2["tramo"].tolist(),
                                   index=df_tri2["tramo"].tolist().index(record["tramo"]), key="edit_tramo")
            fila2 = df_tri2[df_tri2["tramo"] == tramo_e].iloc[0]

            inicio_e = st.text_input("Inicio", value=str(fila2["inicio"]), key="edit_inicio")
            fin_e    = st.text_input("Fin"   , value=str(fila2["fin"])   , key="edit_fin")
            st.text_input("MUFA Origen", value=fila2["mufa_inicio"], disabled=True)
            st.text_input("MUFA Final", value=fila2["mufa_fin"], disabled=True)

            cantidad_e = st.number_input("Cantidad realizada",
                                         min_value=0.0,
                                         value=float(record["cantidad"]),
                                         step=1.0,
                                         key="edit_cant")
            rematado_e = st.slider("% Rematado", 0, 100,
                                   value=int(record["rematado"]), key="edit_rem")

            if st.form_submit_button("Actualizar registro"):
                actualizar_produccion(
                    sel_id,
                    fecha=fecha_e.isoformat(),
                    actividad=actividad_e,
                    trabajador=trabajador_e,
                    triot=triot_e,
                    tramo=tramo_e,
                    inicio=inicio_e,
                    fin=fin_e,
                    mufa_origen=fila2["mufa_inicio"],
                    mufa_final=fila2["mufa_fin"],
                    cantidad=float(cantidad_e),
                    rematado=int(rematado_e)
                )

if __name__ == "__main__":
    app()
