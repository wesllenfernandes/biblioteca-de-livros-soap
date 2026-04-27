import sqlite3
import bcrypt

def init_database():
    """Inicializa o banco de dados SQLite e cria as tabelas de administradores, categorias e cursos"""
    conn = sqlite3.connect('cursos.db')
    cursor = conn.cursor()
    
    # Criar tabela de categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    ''')
    
    # Criar tabela de cursos com foreign key para categoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            carga_horaria INTEGER NOT NULL,
            preco INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    ''')
    
    # Criar tabela de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nome TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Verificar se já existem categorias
    cursor.execute('SELECT COUNT(*) FROM categorias')
    count_categorias = cursor.fetchone()[0]
    
    if count_categorias == 0:
        # Inserir categorias iniciais
        categorias_iniciais = [
            ("Programação", "Cursos de linguagens de programação"),
            ("Web", "Desenvolvimento web front-end e back-end"),
            ("Dados", "Banco de dados e análise de dados"),
        ]
        
        cursor.executemany(
            'INSERT INTO categorias (nome, descricao) VALUES (?, ?)',
            categorias_iniciais
        )
        conn.commit()
        print("3 categorias inseridas na tabela 'categorias'")
    else:
        print(f"Tabela 'categorias' já contém {count_categorias} categorias.")
    
    # Verificar se já existem cursos
    cursor.execute('SELECT COUNT(*) FROM cursos')
    count_cursos = cursor.fetchone()[0]
    
    if count_cursos == 0:
        # Inserir cursos iniciais vinculados às categorias
        cursos_iniciais = [
            ("Python Básico", 1, 40, 200),  # Categoria 1: Programação
            ("Desenvolvimento Web", 2, 60, 350),  # Categoria 2: Web
            ("Banco de Dados", 3, 50, 300),  # Categoria 3: Dados
        ]
        
        cursor.executemany(
            'INSERT INTO cursos (nome, categoria_id, carga_horaria, preco) VALUES (?, ?, ?, ?)',
            cursos_iniciais
        )
        conn.commit()
        print("3 cursos inseridos na tabela 'cursos'")
        print("Banco de dados inicializado com sucesso!")
    else:
        print(f"Tabela 'cursos' já contém {count_cursos} cursos.")
    
    # Verificar se já existem administradores
    cursor.execute('SELECT COUNT(*) FROM administradores')
    count_admins = cursor.fetchone()[0]
    
    if count_admins == 0:
        # Inserir administrador padrão
        senha_padrao = 'admin123'
        senha_hash = bcrypt.hashpw(senha_padrao.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute(
            'INSERT INTO administradores (usuario, senha, nome) VALUES (?, ?, ?)',
            ('admin', senha_hash.decode('utf-8'), 'Administrador Padrão')
        )
        conn.commit()
        print("1 administrador padrão inserido na tabela 'administradores'")
        print(f"Usuário: admin | Senha: {senha_padrao}")
    else:
        print(f"Tabela 'administradores' já contém {count_admins} administradores.")
    
    conn.close()

if __name__ == '__main__':
    init_database()
