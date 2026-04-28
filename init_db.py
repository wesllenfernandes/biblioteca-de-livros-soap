import sqlite3

import bcrypt

DB_PATH = "cursos.db"


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            carga_horaria INTEGER NOT NULL CHECK (carga_horaria > 0),
            preco INTEGER NOT NULL CHECK (preco >= 0),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nome TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
            [
                ("Programacao", "Cursos de linguagens de programacao"),
                ("Web", "Desenvolvimento web front-end e back-end"),
                ("Dados", "Banco de dados e analise de dados"),
            ],
        )
        print("Categorias iniciais inseridas.")

    cursor.execute("SELECT COUNT(*) FROM cursos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """
            INSERT INTO cursos (nome, categoria_id, carga_horaria, preco)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Python Basico", 1, 40, 200),
                ("Desenvolvimento Web", 2, 60, 350),
                ("Banco de Dados", 3, 50, 300),
            ],
        )
        print("Cursos iniciais inseridos.")

    cursor.execute("SELECT COUNT(*) FROM administradores")
    if cursor.fetchone()[0] == 0:
        senha_padrao = "admin123"
        senha_hash = bcrypt.hashpw(senha_padrao.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO administradores (usuario, senha, nome) VALUES (?, ?, ?)",
            ("admin", senha_hash.decode("utf-8"), "Administrador Padrao"),
        )
        print("Administrador padrao criado: usuario=admin senha=admin123")

    conn.commit()
    conn.close()
    print(f"Banco de dados pronto em {DB_PATH}.")


if __name__ == "__main__":
    init_database()
