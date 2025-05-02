
import sqlite3
import hashlib

DB_PATH = "productividad_fibra.db"

def encriptar_contrasena(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reiniciar_tabla_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Eliminar tabla si existe
    cursor.execute("DROP TABLE IF EXISTS usuarios")

    # Crear tabla nueva con columnas correctas
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            contrasena TEXT,
            rol TEXT
        )
    """)

    # Insertar usuario admin por defecto
    admin_pass = encriptar_contrasena("admin123")
    cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                   ("admin", admin_pass, "admin"))

    conn.commit()
    conn.close()
    print("✅ Tabla 'usuarios' reiniciada con éxito.")

if __name__ == "__main__":
    reiniciar_tabla_usuarios()
