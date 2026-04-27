
import sqlite3
import bcrypt
import secrets
from spyne import Application, rpc, ServiceBase, Unicode, Integer, Iterable, ComplexModel, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from werkzeug.serving import run_simple

# Sistema de tokens em memória
tokens_ativos = {}

# Modelo de dados
class Categoria(ComplexModel):
    id = Integer
    nome = Unicode
    descricao = Unicode

class Curso(ComplexModel):
    id = Integer
    nome = Unicode
    categoria_id = Integer
    categoria_nome = Unicode
    carga_horaria = Integer
    preco = Integer

class Administrador(ComplexModel):
    id = Integer
    usuario = Unicode
    nome = Unicode
    criado_em = Unicode

class Token(ComplexModel):
    token = Unicode
    administrador_id = Integer
    administrador_nome = Unicode

# Função auxiliar para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('cursos.db')
    conn.row_factory = sqlite3.Row
    return conn

class CatalogoCursosService(ServiceBase):

    @rpc(_returns=Iterable(Curso))
    def listar_cursos(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.nome, c.categoria_id, cat.nome as categoria_nome, 
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        cursos = []
        for row in rows:
            cursos.append(Curso(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                categoria_nome=row['categoria_nome'],
                carga_horaria=row['carga_horaria'],
                preco=row['preco']
            ))
        return cursos

    @rpc(Integer, _returns=Curso)
    def consultar_curso(ctx, curso_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.nome, c.categoria_id, cat.nome as categoria_nome, 
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
        ''', (curso_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Curso(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                categoria_nome=row['categoria_nome'],
                carga_horaria=row['carga_horaria'],
                preco=row['preco']
            )
        return None

    @rpc(Unicode, _returns=Iterable(Curso))
    def buscar_por_categoria(ctx, categoria):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.nome, c.categoria_id, cat.nome as categoria_nome, 
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE LOWER(cat.nome) = LOWER(?)
        ''', (categoria,))
        rows = cursor.fetchall()
        conn.close()
        
        cursos = []
        for row in rows:
            cursos.append(Curso(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                categoria_nome=row['categoria_nome'],
                carga_horaria=row['carga_horaria'],
                preco=row['preco']
            ))
        return cursos

    @rpc(_returns=Iterable(Categoria))
    def listar_categorias(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categorias')
        rows = cursor.fetchall()
        conn.close()
        
        categorias = []
        for row in rows:
            categorias.append(Categoria(
                id=row['id'],
                nome=row['nome'],
                descricao=row['descricao']
            ))
        return categorias

    @rpc(Unicode, Unicode, _returns=Categoria)
    def cadastrar_categoria(ctx, nome, descricao):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categorias (nome, descricao) VALUES (?, ?)',
                (nome, descricao)
            )
            conn.commit()
            categoria_id = cursor.lastrowid
            
            cursor.execute('SELECT * FROM categorias WHERE id = ?', (categoria_id,))
            row = cursor.fetchone()
            conn.close()
            
            return Categoria(
                id=row['id'],
                nome=row['nome'],
                descricao=row['descricao']
            )
        except sqlite3.IntegrityError:
            conn.close()
            return None

    @rpc(Unicode, Integer, Integer, Integer, _returns=Curso)
    def cadastrar_curso(ctx, nome, categoria_id, carga_horaria, preco):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se a categoria existe
        cursor.execute('SELECT id FROM categorias WHERE id = ?', (categoria_id,))
        if not cursor.fetchone():
            conn.close()
            return None
        
        try:
            cursor.execute(
                'INSERT INTO cursos (nome, categoria_id, carga_horaria, preco) VALUES (?, ?, ?, ?)',
                (nome, categoria_id, carga_horaria, preco)
            )
            conn.commit()
            curso_id = cursor.lastrowid
            
            cursor.execute('''
                SELECT c.id, c.nome, c.categoria_id, cat.nome as categoria_nome, 
                       c.carga_horaria, c.preco
                FROM cursos c
                LEFT JOIN categorias cat ON c.categoria_id = cat.id
                WHERE c.id = ?
            ''', (curso_id,))
            row = cursor.fetchone()
            conn.close()
            
            return Curso(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                categoria_nome=row['categoria_nome'],
                carga_horaria=row['carga_horaria'],
                preco=row['preco']
            )
        except Exception as e:
            conn.close()
            return None

    @rpc(Unicode, Unicode, Unicode, _returns=Administrador)
    def criar_administrador(ctx, usuario, senha, nome):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Hash da senha
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute(
                'INSERT INTO administradores (usuario, senha, nome) VALUES (?, ?, ?)',
                (usuario, senha_hash.decode('utf-8'), nome)
            )
            conn.commit()
            admin_id = cursor.lastrowid
            
            cursor.execute('SELECT id, usuario, nome, criado_em FROM administradores WHERE id = ?', (admin_id,))
            row = cursor.fetchone()
            conn.close()
            
            return Administrador(
                id=row['id'],
                usuario=row['usuario'],
                nome=row['nome'],
                criado_em=row['criado_em']
            )
        except sqlite3.IntegrityError:
            conn.close()
            return None

    @rpc(Unicode, Unicode, _returns=Token)
    def login(ctx, usuario, senha):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, usuario, senha, nome, criado_em FROM administradores WHERE usuario = ?', (usuario,))
        row = cursor.fetchone()
        conn.close()
        
        if row and bcrypt.checkpw(senha.encode('utf-8'), row['senha'].encode('utf-8')):
            # Gerar token seguro
            token = secrets.token_hex(32)
            tokens_ativos[token] = row['id']
            
            return Token(
                token=token,
                administrador_id=row['id'],
                administrador_nome=row['nome']
            )
        return None

    @rpc(Unicode, _returns=Boolean)
    def validar_token(ctx, token):
        return token in tokens_ativos

    @rpc(Unicode, _returns=Boolean)
    def logout(ctx, token):
        if token in tokens_ativos:
            del tokens_ativos[token]
            return True
        return False

application = Application(
    [CatalogoCursosService],
    tns='http://exemplo.com/catalogocursos',
    in_protocol=Soap11(),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    print("Servidor rodando em http://localhost:8000")
    print("WSDL disponível em http://localhost:8000/?wsdl")
    run_simple('0.0.0.0', 8000, wsgi_app)
