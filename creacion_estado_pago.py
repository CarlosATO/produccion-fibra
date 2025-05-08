import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from config import supabase

# --- Funciones de acceso a datos en Supabase ---
def leer_empresas():
    resp = supabase.table("empresas").select("nombre").order("nombre").execute()
    return [r["nombre"] for r in resp.data]


def leer_produccion(empresa_sel):
    # Obtiene producción, personal y actividades
    prod = pd.DataFrame(
        supabase.table("produccion").select("id, fecha, actividad, cantidad, trabajador").execute().data
    )
    perso = pd.DataFrame(
        supabase.table("personal").select("nombre, empresa").execute().data
    )
    acts = pd.DataFrame(
        supabase.table("actividades").select("descripcion, valor_produccion, valor_venta").execute().data
    )
    # Merge para agregar valores
    df = prod.merge(perso, left_on="trabajador", right_on="nombre")
    df = df[df["empresa"] == empresa_sel]
    df = df.merge(acts, left_on="actividad", right_on="descripcion")
    # Excluir ya pagados
    pagos = supabase.table("estados_pago_detalle").select("produccion_id").execute().data
    pagados = {r["produccion_id"] for r in pagos}
    df = df[~df["id"].isin(pagados)]
    # Cálculo de montos
    df["Monto Producción"] = df["cantidad"] * df["valor_produccion"]
    df["Monto Venta"] = df["cantidad"] * df["valor_venta"]
    return df


def leer_gastos(empresa_sel):
    g = pd.DataFrame(
        supabase.table("gastos").select("id, fecha, detalle, monto, empresa").execute().data
    )
    df_g = g[g["empresa"] == empresa_sel].copy()
    usados = supabase.table("estados_pago_gastos").select("gasto_id").execute().data
    usados_ids = {r["gasto_id"] for r in usados}
    df_g = df_g[~df_g["id"].isin(usados_ids)]
    df_g = df_g.rename(columns={"detalle": "descripcion"})
    return df_g


# --- Generación de PDF en memoria ---
def generar_pdf_bytes(
    correlativo: str,
    empresa: str,
    fecha: str,
    df_prod: pd.DataFrame,
    df_gast: pd.DataFrame,
    total_prod: float,
    total_venta: float,
    total_gastos: float,
    neto: float
) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"ESTADO DE PAGO {correlativo}", ln=True, align="C")
    pdf.ln(5)

    # Datos generales
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(40, 8, "Empresa:")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, empresa, ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(40, 8, "Fecha:")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, fecha, ln=True)
    pdf.ln(5)

    # Tabla de Producción
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(80, 8, "Actividad", border=1)
    pdf.cell(30, 8, "Cantidad", border=1, align="R")
    pdf.cell(40, 8, "Total Prod.", border=1, align="R")
    pdf.cell(40, 8, "Total Venta", border=1, align="R")
    pdf.ln()
    pdf.set_font("Helvetica", "", 11)
    for _, r in df_prod.iterrows():
        pdf.cell(80, 7, r["actividad"], border=1)
        pdf.cell(30, 7, str(int(r["cantidad"])), border=1, align="R")
        pdf.cell(40, 7, f"$ {r['Monto Producción']:,.0f}", border=1, align="R")
        pdf.cell(40, 7, f"$ {r['Monto Venta']:,.0f}", border=1, align="R")
        pdf.ln()
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(150, 8, "Total Producción", border=1, align="R")
    pdf.cell(40, 8, f"$ {total_prod:,.0f}", border=1, align="R")
    pdf.ln(12)

    # Tabla de Gastos
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(60, 8, "Fecha", border=1)
    pdf.cell(85, 8, "Detalle", border=1)
    pdf.cell(45, 8, "Monto", border=1, align="R")
    pdf.ln()
    pdf.set_font("Helvetica", "", 11)
    for _, g in df_gast.iterrows():
        pdf.cell(60, 7, g["fecha"], border=1)
        pdf.cell(85, 7, g["descripcion"], border=1)
        pdf.cell(45, 7, f"$ {g['monto']:,.0f}", border=1, align="R")
        pdf.ln()
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(145, 8, "Total Gastos", border=1, align="R")
    pdf.cell(45, 8, f"$ {total_gastos:,.0f}", border=1, align="R")
    pdf.ln(12)

    # Resumen
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "NETO A PAGAR", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 6, "Monto Neto:")
    pdf.cell(0, 6, f"$ {neto:,.0f}", ln=True)
    pdf.ln(10)

    # Pie de página de autorización
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_width, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "SE AUTORIZA A FACTURAR A", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "SOMYL S.A.", ln=True)
    pdf.cell(0, 6, "RUT: 76.002.581-K", ln=True)
    pdf.multi_cell(0, 6, "Dirección: Puerta Oriente 361 Of. 311 B, Torre B, Colina")
    pdf.ln(2)
    pdf.cell(30, 6, "AUTORIZA:")
    pdf.cell(0, 6, "Luis Medina", ln=True)
    pdf.cell(30, 6, "CORREO:")
    pdf.cell(0, 6, "lmedina@somyl.com", ln=True)
    pdf.ln(2)
    pdf.cell(35, 6, "ENVIAR FACTURA A:")
    pdf.multi_cell(0, 6, "cynthia.miranda@somyl.com; carlos.alegria@somyl.com")

    return pdf.output(dest="S").encode("latin1")


# --- Inserción de Estado de Pago en Supabase ---
def insertar_estado_pago(nuevo_corr: str, empresa_sel: str,
                          total_prod: float, total_venta: float,
                          total_gastos: float, neto: float):
    # Cabecera
    supabase.table("estados_pago").insert({
        "correlativo": nuevo_corr,
        "fecha": datetime.date.today().isoformat(),
        "empresa": empresa_sel,
        "total_produccion": total_prod,
        "total_venta": total_venta,
        "total_gastos": total_gastos,
        "neto": neto
    }).execute()
    # Detalle producción
    supabase.table("estados_pago_detalle").insert([
        {"correlativo": nuevo_corr, "produccion_id": i}
        for i in st.session_state['seleccionadas']
    ]).execute()
    # Detalle gastos
    supabase.table("estados_pago_gastos").insert([
        {"correlativo": nuevo_corr, "gasto_id": i}
        for i in st.session_state['gastos_seleccionadas']
    ]).execute()


# --- Función principal de Streamlit ---
def app():
    st.subheader("🧾 Creación de Estado de Pago")

    # 1) Lista de empresas
    empresas = leer_empresas()
    if not empresas:
        st.warning("⚠️ No hay empresas registradas en Supabase.")
        return
    empresa_sel = st.selectbox("Selecciona Subcontrato", empresas)

    # 2) Datos de producción y gastos
    df_prod = leer_produccion(empresa_sel)
    df_g = leer_gastos(empresa_sel)
    if df_prod.empty and df_g.empty:
        st.info("No hay datos disponibles.")
        return

    # Cálculo montos y setup de session_state
    total_prod = df_prod['Monto Producción'].sum()
    total_venta = df_prod['Monto Venta'].sum()
    total_gastos = df_g['monto'].sum()
    neto = total_prod - total_gastos

    if ('disponibles' not in st.session_state
            or st.session_state.get('last_empresa') != empresa_sel):
        st.session_state['last_empresa'] = empresa_sel
        st.session_state['disponibles'] = df_prod['id'].tolist()
        st.session_state['seleccionadas'] = []
        st.session_state['gastos_disponibles'] = df_g['id'].tolist()
        st.session_state['gastos_seleccionadas'] = []

    # 3) Dual-listbox Producción
    row_map = {r['id']: r for _, r in df_prod.iterrows()}
    c1, c2 = st.columns(2)
    with c1:
        sel_disp = st.multiselect(
            "Líneas disponibles", st.session_state['disponibles'],
            format_func=lambda i: f"{row_map[i]['fecha']} | {row_map[i]['actividad']} | QTY:{int(row_map[i]['cantidad'])} | Prod:${row_map[i]['Monto Producción']:,.0f} | Venta:${row_map[i]['Monto Venta']:,.0f}",
            key='d1'
        )
        if st.button('>> Añadir', key='a1'):
            for i in sel_disp:
                st.session_state['disponibles'].remove(i)
                st.session_state['seleccionadas'].append(i)
    with c2:
        sel_sel = st.multiselect(
            "Líneas seleccionadas", st.session_state['seleccionadas'],
            format_func=lambda i: f"{row_map[i]['fecha']} | {row_map[i]['actividad']} | QTY:{int(row_map[i]['cantidad'])} | Prod:${row_map[i]['Monto Producción']:,.0f} | Venta:${row_map[i]['Monto Venta']:,.0f}",
            key='s1'
        )
        if st.button('<< Quitar', key='q1'):
            for i in sel_sel:
                st.session_state['seleccionadas'].remove(i)
                st.session_state['disponibles'].append(i)

    # 4) Dual-listbox Gastos
    st.markdown("---")
    st.subheader("💸 Gastos a descontar")
    row_g_map = {g['id']: g for _, g in df_g.iterrows()}
    c3, c4 = st.columns(2)
    with c3:
        sel_g_disp = st.multiselect(
            "Gastos disponibles", st.session_state['gastos_disponibles'],
            format_func=lambda i: f"{row_g_map[i]['fecha']} | {row_g_map[i]['descripcion']} | Monto:${row_g_map[i]['monto']:,.0f}",
            key='gd1'
        )
        if st.button('>> Añadir Gasto', key='ag1'):
            for i in sel_g_disp:
                st.session_state['gastos_disponibles'].remove(i)
                st.session_state['gastos_seleccionadas'].append(i)
    with c4:
        sel_g_sel = st.multiselect(
            "Gastos seleccionados", st.session_state['gastos_seleccionadas'],
            format_func=lambda i: f"{row_g_map[i]['fecha']} | {row_g_map[i]['descripcion']} | Monto:${row_g_map[i]['monto']:,.0f}",
            key='gs1'
        )
        if st.button('<< Quitar Gasto', key='qg1'):
            for i in sel_g_sel:
                st.session_state['gastos_seleccionadas'].remove(i)
                st.session_state['gastos_disponibles'].append(i)

    # 5) Mostrar métricas y detalle Gastos
    st.markdown("---")
    col_tot, col_det = st.columns([1, 1])
    with col_tot:
        st.metric("Total Producción", f"$ {total_prod:,.0f}")
        st.metric("Total Venta", f"$ {total_venta:,.0f}")
        st.metric("Total Gastos", f"$ {total_gastos:,.0f}")
        st.metric("Neto", f"$ {neto:,.0f}")
    with col_det:
        st.markdown("### Detalle Gastos")
        detalle = df_g[['fecha', 'descripcion', 'monto']].rename(
            columns={'fecha': 'Fecha', 'descripcion': 'Detalle', 'monto': 'Monto'}
        )
        st.dataframe(detalle, use_container_width=True, hide_index=True)

    # 6) Previsualizar PDF
    if st.button('📄 Previsualizar PDF', key='pv'):
        # Obtener siguiente correlativo
        corr_resp = supabase.table("estados_pago").select("correlativo").order("correlativo", desc=True).limit(1).execute().data
        num = int(corr_resp[0]['correlativo'].split('-')[1]) if corr_resp else 0
        temp_corr = f"EGTD-{num+1:02d}"
        hoy = datetime.date.today().isoformat()
        pdf_bytes = generar_pdf_bytes(
            temp_corr, empresa_sel, hoy,
            df_prod[df_prod['id'].isin(st.session_state['seleccionadas'])],
            df_g[df_g['id'].isin(st.session_state['gastos_seleccionadas'])],
            total_prod, total_venta, total_gastos, neto
        )
        st.download_button(
            label="Descargar Previsualización PDF",
            data=pdf_bytes,
            file_name=f"{temp_corr}_preview.pdf",
            mime="application/pdf"
        )

    # 7) Guardar Estado de Pago
    if st.button('💾 Guardar Estado de Pago', key='sv'):
        corr_resp = supabase.table("estados_pago").select("correlativo").order("correlativo", desc=True).limit(1).execute().data
        num = int(corr_resp[0]['correlativo'].split('-')[1]) if corr_resp else 0
        nuevo_corr = f"EGTD-{num+1:02d}"
        insertar_estado_pago(nuevo_corr, empresa_sel, total_prod, total_venta, total_gastos, neto)
        st.success(f"✅ Estado de Pago **{nuevo_corr}** guardado en Supabase.")
        # Reset session
        st.session_state['last_empresa'] = None


if __name__ == "__main__":
    app()
