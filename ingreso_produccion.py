import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Creación de tabla producción ---
def crear_tabla_produccion():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            actividad TEXT,
            trabajador TEXT,
            triot TEXT,
            tramo TEXT,
            inicio TEXT,
            fin TEXT,
            mufa_origen TEXT,
            mufa_final TEXT,
            cantidad REAL,
            rematado REAL
        )
    """
    )
    conn.commit()
    conn.close()

# --- Consultas genéricas ---
def obtener_datos_tabla(tabla):
    conn = conectar()
    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
    conn.close()
    return df

# --- Operaciones CRUD para producción ---
def guardar_produccion(
    fecha, actividad, trabajador,
    triot, tramo,
    inicio, fin,
    mufa_o, mufa_f,
    cantidad, rematado
):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO produccion (
            fecha, actividad, trabajador,
            triot, tramo,
            inicio, fin,
            mufa_origen, mufa_final,
            cantidad, rematado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fecha, actividad, trabajador,
            triot, tramo,
            inicio, fin,
            mufa_o, mufa_f,
            cantidad, rematado
        ),
    )
    conn.commit()
    conn.close()
    st.success("✅ Producción registrada.")


def actualizar_produccion(
    id_prod, fecha, actividad, trabajador,
    triot, tramo,
    inicio, fin,
    mufa_o, mufa_f,
    cantidad, rematado
):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE produccion SET
            fecha = ?, actividad = ?, trabajador = ?,
            triot = ?, tramo = ?,
            inicio = ?, fin = ?,
            mufa_origen = ?, mufa_final = ?,
            cantidad = ?, rematado = ?
        WHERE id = ?
        """,
        (
            fecha, actividad, trabajador,
            triot, tramo,
            inicio, fin,
            mufa_o, mufa_f,
            cantidad, rematado,
            id_prod,
        ),
    )
    conn.commit()
    conn.close()
    st.success("✏️ Registro actualizado.")

# --- Interfaz de usuario ---
def app():
    st.subheader("📥 Ingreso de Producción")
    crear_tabla_produccion()

    # Reset de campos tras submit
    if st.session_state.get('reset_form'):
        for key in ['inicio', 'fin', 'cantidad', 'rematado']:
            st.session_state.pop(key, None)
        st.session_state['reset_form'] = False

    # Carga de catálogos
    df_actividades = obtener_datos_tabla("actividades")
    df_personal = obtener_datos_tabla("personal")
    df_tramos = obtener_datos_tabla("tramos")

    with st.form("formulario_produccion"):
        fecha = st.date_input("Fecha", value=date.today(), key="fecha")
        actividad = st.selectbox(
            "Actividad",
            df_actividades["descripcion"].tolist(),
            key="actividad"
        )
        trabajador = st.selectbox(
            "Trabajador",
            df_personal["nombre"].tolist(),
            key="trabajador"
        )
        triot = st.selectbox(
            "TRIOT",
            df_tramos["triot"].unique().tolist(),
            key="triot"
        )
        tramo = st.selectbox(
            "Tramo",
            df_tramos[df_tramos["triot"] == triot]["tramo"].tolist(),
            key="tramo"
        )

        # Obtener valores por defecto de tramo
        sel = df_tramos[
            (df_tramos["triot"] == triot) &
            (df_tramos["tramo"] == tramo)
        ]
        inicio_val = sel["inicio"].iloc[0] if not sel.empty else ""
        fin_val = sel["fin"].iloc[0] if not sel.empty else ""
        mufa_o = sel["mufa_inicio"].iloc[0] if not sel.empty else ""
        mufa_f = sel["mufa_fin"].iloc[0] if not sel.empty else ""

        inicio = st.text_input(
            "Inicio (metros)",
            value=str(inicio_val),
            key="inicio"
        )
        fin = st.text_input(
            "Fin (metros)",
            value=str(fin_val),
            key="fin"
        )
        st.text_input("MUFA Origen", value=str(mufa_o), disabled=True)
        st.text_input("MUFA Final", value=str(mufa_f), disabled=True)

        cantidad = st.number_input(
            "Cantidad realizada",
            min_value=0.0,
            step=1.0,
            key="cantidad"
        )
        rematado = st.slider(
            "% Rematado",
            0,
            100,
            key="rematado"
        )

        submitted = st.form_submit_button("Registrar producción")
        if submitted:
            guardar_produccion(
                str(fecha), actividad, trabajador,
                triot, tramo,
                inicio, fin,
                mufa_o, mufa_f,
                cantidad, rematado
            )
            st.session_state['reset_form'] = True
            # Forzar rerun para actualizar UI y mostrar historial
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
            elif hasattr(st, 'script_request_rerun'):
                st.script_request_rerun()
            else:
                return

    st.markdown("---")
    st.subheader("📄 Historial de producción")
    df_historial = obtener_datos_tabla("produccion")
    st.dataframe(df_historial, use_container_width=True)

    st.markdown("---")
    st.subheader("✏️ Editar registro existente")
    if not df_historial.empty:
        ids = df_historial["id"].tolist()
        selected_id = st.selectbox(
            "Selecciona el ID a editar", ids, key="edit_id"
        )
        registro = df_historial[df_historial["id"] == selected_id].iloc[0]

        with st.form("editar_produccion"):
            fecha_e = st.date_input(
                "Fecha",
                value=pd.to_datetime(registro["fecha"]).date(),
                key="edit_fecha"
            )
            actividad_e = st.selectbox(
                "Actividad",
                df_actividades["descripcion"].tolist(),
                index=df_actividades["descripcion"].tolist().index(registro["actividad"]),
                key="edit_actividad"
            )
            trabajador_e = st.selectbox(
                "Trabajador",
                df_personal["nombre"].tolist(),
                index=df_personal["nombre"].tolist().index(registro["trabajador"]),
                key="edit_trabajador"
            )
            triot_e = st.selectbox(
                "TRIOT",
                df_tramos["triot"].unique().tolist(),
                index=list(df_tramos["triot"].unique()).index(registro["triot"]),
                key="edit_triot"
            )
            tramo_e = st.selectbox(
                "Tramo",
                df_tramos[df_tramos["triot"] == triot_e]["tramo"].tolist(),
                index=df_tramos[df_tramos["triot"] == triot_e]["tramo"].tolist().index(registro["tramo"]),
                key="edit_tramo"
            )

            inicio_e = st.text_input(
                "Inicio (metros)", value=str(registro["inicio"]), key="edit_inicio"
            )
            fin_e = st.text_input(
                "Fin (metros)", value=str(registro["fin"]), key="edit_fin"
            )
            st.text_input("MUFA Origen", value=registro["mufa_origen"], disabled=True)
            st.text_input("MUFA Final", value=registro["mufa_final"], disabled=True)
            cantidad_e = st.number_input(
                "Cantidad realizada",
                value=registro["cantidad"],
                step=1.0,
                key="edit_cantidad"
            )
            rematado_e = st.slider(
                "% Rematado",
                0,
                100,
                value=int(registro["rematado"]),
                key="edit_rematado"
            )

            editar = st.form_submit_button("Actualizar registro")
            if editar:
                actualizar_produccion(
                    selected_id,
                    str(fecha_e), actividad_e, trabajador_e,
                    triot_e, tramo_e,
                    inicio_e, fin_e,
                    registro["mufa_origen"], registro["mufa_final"],
                    cantidad_e, rematado_e
                )
                return

if __name__ == "__main__":
    app()
