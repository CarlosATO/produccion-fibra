import streamlit as st
import sqlite3
import pandas as pd
import datetime
from fpdf import FPDF

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

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

    # Nota de Autorización al pie
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

# --- Función principal de Streamlit ---
def app():
    st.subheader("🧾 Creación de Estado de Pago")

    # BD y tablas
    conn = conectar()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS estados_pago (
            correlativo TEXT PRIMARY KEY,
            fecha TEXT,
            empresa TEXT,
            total_produccion REAL,
            total_venta REAL,
            total_gastos REAL,
            neto REAL
        );
        CREATE TABLE IF NOT EXISTS estados_pago_detalle (
            correlativo TEXT,
            produccion_id INTEGER,
            PRIMARY KEY(correlativo, produccion_id)
        );
        CREATE TABLE IF NOT EXISTS estados_pago_gastos (
            correlativo TEXT,
            gasto_id INTEGER,
            PRIMARY KEY(correlativo, gasto_id)
        );
    """)
    conn.commit()

    # Subcontratos
    df_emp = pd.read_sql_query("SELECT nombre FROM empresas ORDER BY nombre", conn)
    empresas = df_emp["nombre"].tolist()
    if not empresas:
        st.warning("⚠️ No hay empresas registradas.")
        conn.close()
        return
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        empresa_sel = st.selectbox("Selecciona Subcontrato", empresas)

    # Datos filtrados
    df = pd.read_sql_query("""
        SELECT pr.id, pr.fecha, pr.actividad, pr.cantidad,
               a.valor_produccion, a.valor_venta
          FROM produccion pr
          JOIN personal pe ON pr.trabajador = pe.nombre
          JOIN actividades a ON pr.actividad = a.descripcion
         WHERE pe.empresa = ?
           AND pr.id NOT IN (SELECT produccion_id FROM estados_pago_detalle)
    """, conn, params=(empresa_sel,))
    df_g = pd.read_sql_query("""
        SELECT id, fecha, detalle AS descripcion, monto
          FROM gastos
         WHERE empresa = ?
           AND id NOT IN (SELECT gasto_id FROM estados_pago_gastos)
    """, conn, params=(empresa_sel,))
    if df.empty and df_g.empty:
        st.info("No hay datos disponibles.")
        conn.close()
        return

    df["Monto Producción"] = df["cantidad"] * df["valor_produccion"]
    df["Monto Venta"] = df["cantidad"] * df["valor_venta"]

    # Reset session_state al cambiar subcontrato
    if ('last_empresa' not in st.session_state or st.session_state['last_empresa'] != empresa_sel):
        st.session_state['last_empresa'] = empresa_sel
        st.session_state['disponibles'] = df['id'].tolist()
        st.session_state['seleccionadas'] = []
        st.session_state['gastos_disponibles'] = df_g['id'].tolist()
        st.session_state['gastos_seleccionadas'] = []

    # Formateo de opciones
    row_map = {r['id']: r for _, r in df.iterrows()}
    gas_map = {r['id']: r for _, r in df_g.iterrows()}
    def fmt_line(i):
        r = row_map[i]
        return f"{r['fecha']} | {r['actividad']} | QTY:{int(r['cantidad'])} | Prod:${r['Monto Producción']:,.0f} | Venta:${r['Monto Venta']:,.0f}"
    def fmt_gas(i):
        g = gas_map[i]
        return f"{g['fecha']} | {g['descripcion']} | Monto:${g['monto']:,.0f}"

    # Dual-listbox de Producción
    c1, c2 = st.columns(2)
    with c1:
        sel_disp = st.multiselect(
            "Líneas disponibles",
            st.session_state['disponibles'],
            format_func=fmt_line,
            key='d1'
        )
        if st.button('>> Añadir', key='a1'):
            for i in sel_disp:
                st.session_state['disponibles'].remove(i)
                st.session_state['seleccionadas'].append(i)
    with c2:
        sel_sel = st.multiselect(
            "Líneas seleccionadas",
            st.session_state['seleccionadas'],
            format_func=fmt_line,
            key='s1'
        )
        if st.button('<< Quitar', key='q1'):
            for i in sel_sel:
                st.session_state['seleccionadas'].remove(i)
                st.session_state['disponibles'].append(i)

    # Dual-listbox de Gastos
    st.markdown("---")
    st.subheader("💸 Gastos a descontar")
    c3, c4 = st.columns(2)
    with c3:
        sel_g_disp = st.multiselect(
            "Gastos disponibles",
            st.session_state['gastos_disponibles'],
            format_func=fmt_gas,
            key='gd1'
        )
        if st.button('>> Añadir Gasto', key='ag1'):
            for i in sel_g_disp:
                st.session_state['gastos_disponibles'].remove(i)
                st.session_state['gastos_seleccionadas'].append(i)
    with c4:
        sel_g_sel = st.multiselect(
            "Gastos seleccionados",
            st.session_state['gastos_seleccionadas'],
            format_func=fmt_gas,
            key='gs1'
        )
        if st.button('<< Quitar Gasto', key='qg1'):
            for i in sel_g_sel:
                st.session_state['gastos_seleccionadas'].remove(i)
                st.session_state['gastos_disponibles'].append(i)

    # Cálculo de totales
    df_sel = df[df['id'].isin(st.session_state['seleccionadas'])]
    df_g_sel = df_g[df_g['id'].isin(st.session_state['gastos_seleccionadas'])]
    total_prod = df_sel['Monto Producción'].sum()
    total_venta = df_sel['Monto Venta'].sum()
    total_gastos = df_g_sel['monto'].sum()
    neto = total_prod - total_gastos

    st.markdown("---")
    col_tot, col_det = st.columns([1, 1])
    with col_tot:
        st.metric("Total Producción", f"$ {total_prod:,.0f}")
        st.metric("Total Venta", f"$ {total_venta:,.0f}")
        st.metric("Total Gastos", f"$ {total_gastos:,.0f}")
        st.metric("Neto", f"$ {neto:,.0f}")
    with col_det:
        st.markdown("### Detalle Gastos")
        detalle = df_g_sel[['fecha', 'descripcion', 'monto']].rename(
            columns={'fecha': 'Fecha', 'descripcion': 'Detalle', 'monto': 'Monto'}
        )
        st.dataframe(detalle, use_container_width=True, hide_index=True)

    # Botón de Previsualizar PDF
    if st.button('📄 Previsualizar PDF', key='pv'):
        cur.execute("SELECT correlativo FROM estados_pago ORDER BY correlativo DESC LIMIT 1")
        fila = cur.fetchone()
        num = int(fila[0].split('-')[1]) if fila else 0
        temp_corr = f"EGTD-{(num+1):02d}"
        hoy = datetime.date.today().isoformat()
        pdf_bytes = generar_pdf_bytes(
            temp_corr,
            empresa_sel,
            hoy,
            df_sel,
            df_g_sel,
            total_prod,
            total_venta,
            total_gastos,
            neto
        )
        st.download_button(
            label="Descargar Previsualización PDF",
            data=pdf_bytes,
            file_name=f"{temp_corr}_preview.pdf",
            mime="application/pdf"
        )

    # Botón de Guardar Estado de Pago
    if st.button('💾 Guardar Estado de Pago', key='sv'):
        cur.execute("SELECT correlativo FROM estados_pago ORDER BY correlativo DESC LIMIT 1")
        fila = cur.fetchone()
        num = int(fila[0].split('-')[1]) if fila else 0
        num += 1
        nuevo_corr = f"EGTD-{num:02d}"
        hoy = datetime.date.today().isoformat()
        cur.execute(
            "INSERT INTO estados_pago (correlativo, fecha, empresa, total_produccion, total_venta, total_gastos, neto) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nuevo_corr, hoy, empresa_sel, total_prod, total_venta, total_gastos, neto)
        )
        cur.executemany(
            "INSERT INTO estados_pago_detalle (correlativo, produccion_id) VALUES (?, ?)",
            [(nuevo_corr, i) for i in st.session_state['seleccionadas']]
        )
        cur.executemany(
            "INSERT INTO estados_pago_gastos (correlativo, gasto_id) VALUES (?, ?)",
            [(nuevo_corr, i) for i in st.session_state['gastos_seleccionadas']]
        )
        conn.commit()
        st.success(f"✅ Estado de Pago **{nuevo_corr}** guardado.")
        st.session_state['last_empresa'] = None
        conn.close()
        return

    conn.close()

if __name__ == "__main__":
    app()
