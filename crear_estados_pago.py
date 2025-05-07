import sqlite3

conn = sqlite3.connect("productividad_fibra.db")
cur  = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS estados_pago (
        correlativo      TEXT PRIMARY KEY,
        fecha            TEXT,
        empresa          TEXT,
        total_produccion REAL,
        total_venta      REAL,
        total_gastos     REAL,
        neto             REAL
    );
""")

conn.commit()
conn.close()
print("✅ Tabla 'estados_pago' creada (o ya existía).")
