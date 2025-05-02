import sqlite3

DB_PATH = "productividad_fibra.db"

def reiniciar_tabla():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Elimina la tabla si existe
    cursor.execute("DROP TABLE IF EXISTS actividades")

    # Crea la tabla con todas las columnas necesarias
    cursor.execute("""
        CREATE TABLE actividades (
            codigo TEXT PRIMARY KEY,
            grupo TEXT,
            descripcion TEXT,
            unidad TEXT,
            tipo TEXT,
            valor REAL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Tabla 'actividades' reiniciada correctamente.")

if __name__ == "__main__":
    reiniciar_tabla()
