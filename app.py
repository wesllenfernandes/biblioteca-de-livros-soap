import logging
import io
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from lxml import etree
from spyne import Application, ComplexModel, Integer, Iterable, ServiceBase, Unicode, rpc
from spyne.model.fault import Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import WSGIRequestHandler, make_server

DB_PATH = "cursos.db"
LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "catalogo_soap.log")
PORT = int(os.environ.get("PORT", "8010"))
JWT_SECRET = os.environ.get("CATALOGO_JWT_SECRET", "troque-esta-chave-em-producao")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 2
TNS = "http://exemplo.com/catalogocursos"
SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"
WSSE_NS = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("catalogo_cursos_soap")
PROTECTED_OPERATIONS = {
    "cadastrar_categoria",
    "atualizar_categoria",
    "remover_categoria",
    "cadastrar_curso",
    "atualizar_curso",
    "remover_curso",
    "validar_token",
}


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
    tipo = Unicode
    expira_em = Unicode
    administrador_id = Integer
    administrador_nome = Unicode


class ResultadoOperacao(ComplexModel):
    sucesso = Unicode
    mensagem = Unicode


class SecurityHeader(ComplexModel):
    token = Unicode


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def operation_name(ctx):
    descriptor = getattr(ctx, "descriptor", None)
    return getattr(descriptor, "name", "operacao_desconhecida")


def remote_addr(ctx):
    transport = getattr(ctx, "transport", None)
    req_env = getattr(transport, "req_env", {}) if transport else {}
    return req_env.get("REMOTE_ADDR", "desconhecido")


def log_event(ctx, level, message):
    logger.log(level, "[%s] ip=%s %s", operation_name(ctx), remote_addr(ctx), message)


def build_curso(row):
    if row is None:
        return None
    return Curso(
        id=row["id"],
        nome=row["nome"],
        categoria_id=row["categoria_id"],
        categoria_nome=row["categoria_nome"],
        carga_horaria=row["carga_horaria"],
        preco=row["preco"],
    )


def build_categoria(row):
    if row is None:
        return None
    return Categoria(id=row["id"], nome=row["nome"], descricao=row["descricao"])


def generate_token(admin_row):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(admin_row["id"]),
        "usuario": admin_row["usuario"],
        "nome": admin_row["nome"],
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at.isoformat()


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise Fault(faultcode="Client.Auth", faultstring="Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise Fault(faultcode="Client.Auth", faultstring="Token JWT invalido.") from exc


def extract_wsse_token_from_ctx(ctx):
    in_document = getattr(ctx, "in_document", None)
    if in_document is None:
        return None

    try:
        ns = {"soap": SOAP_ENV_NS, "wsse": WSSE_NS}
        token = in_document.findtext("soap:Header/wsse:Security/wsse:BinarySecurityToken", namespaces=ns)
        if isinstance(token, str) and token.strip():
            return token.strip()
    except Exception:
        return None

    return None


def require_authentication(ctx):
    transport = getattr(ctx, "transport", None)
    req_env = getattr(transport, "req_env", {}) if transport else {}
    authenticated_payload = req_env.get("HTTP_X_AUTHENTICATED_PAYLOAD")
    if authenticated_payload:
        payload = decode_token(authenticated_payload)
        ctx.udc = payload
        return payload
    token = extract_wsse_token_from_ctx(ctx)
    if token is None:
        header = getattr(ctx, "in_header", None)
        token = getattr(header, "token", None) if header else None
    if not isinstance(token, str) or not token.strip():
        raise Fault(
            faultcode="Client.Auth",
            faultstring="Cabecalho SOAP de seguranca ausente. Informe wsse:Security/wsse:BinarySecurityToken.",
        )
    payload = decode_token(token)
    ctx.udc = payload
    log_event(ctx, logging.INFO, f"autenticado usuario={payload.get('usuario')}")
    return payload


class CatalogoCursosService(ServiceBase):
    __in_header__ = (SecurityHeader,)

    @rpc(_returns=Iterable(Curso))
    def listar_cursos(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.nome, c.categoria_id, cat.nome AS categoria_nome,
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            ORDER BY c.id
            """
        )
        cursos = [build_curso(row) for row in cursor.fetchall()]
        conn.close()
        log_event(ctx, logging.INFO, f"retornou {len(cursos)} cursos")
        return cursos

    @rpc(Integer, _returns=Curso)
    def consultar_curso(ctx, curso_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.nome, c.categoria_id, cat.nome AS categoria_nome,
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
            """,
            (curso_id,),
        )
        curso = build_curso(cursor.fetchone())
        conn.close()
        if curso is None:
            log_event(ctx, logging.WARNING, f"curso_id={curso_id} nao encontrado")
            raise Fault(faultcode="Client", faultstring="Curso nao encontrado.")
        log_event(ctx, logging.INFO, f"curso_id={curso_id} consultado")
        return curso

    @rpc(Unicode, _returns=Iterable(Curso))
    def buscar_por_categoria(ctx, categoria):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.nome, c.categoria_id, cat.nome AS categoria_nome,
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE LOWER(cat.nome) = LOWER(?)
            ORDER BY c.id
            """,
            (categoria,),
        )
        cursos = [build_curso(row) for row in cursor.fetchall()]
        conn.close()
        log_event(ctx, logging.INFO, f"categoria={categoria} retornou {len(cursos)} cursos")
        return cursos

    @rpc(_returns=Iterable(Categoria))
    def listar_categorias(ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM categorias ORDER BY id")
        categorias = [build_categoria(row) for row in cursor.fetchall()]
        conn.close()
        log_event(ctx, logging.INFO, f"retornou {len(categorias)} categorias")
        return categorias

    @rpc(Integer, _returns=Categoria)
    def consultar_categoria(ctx, categoria_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, descricao FROM categorias WHERE id = ?",
            (categoria_id,),
        )
        categoria = build_categoria(cursor.fetchone())
        conn.close()
        if categoria is None:
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} nao encontrada")
            raise Fault(faultcode="Client", faultstring="Categoria nao encontrada.")
        log_event(ctx, logging.INFO, f"categoria_id={categoria_id} consultada")
        return categoria

    @rpc(Unicode, Unicode, _in_header=(SecurityHeader,), _returns=Categoria)
    def cadastrar_categoria(ctx, nome, descricao):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
                (nome, descricao),
            )
            conn.commit()
            categoria_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, nome, descricao FROM categorias WHERE id = ?",
                (categoria_id,),
            )
            categoria = build_categoria(cursor.fetchone())
            log_event(ctx, logging.INFO, f"categoria criada id={categoria_id}")
            return categoria
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            log_event(ctx, logging.ERROR, f"falha ao criar categoria nome={nome}: {exc}")
            raise Fault(faultcode="Client.Data", faultstring="Categoria ja cadastrada.") from exc
        finally:
            conn.close()

    @rpc(Integer, Unicode, Unicode, _in_header=(SecurityHeader,), _returns=Categoria)
    def atualizar_categoria(ctx, categoria_id, nome, descricao):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorias WHERE id = ?", (categoria_id,))
        if cursor.fetchone() is None:
            conn.close()
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} nao encontrada para atualizacao")
            raise Fault(faultcode="Client", faultstring="Categoria nao encontrada.")
        try:
            cursor.execute(
                "UPDATE categorias SET nome = ?, descricao = ? WHERE id = ?",
                (nome, descricao, categoria_id),
            )
            conn.commit()
            cursor.execute(
                "SELECT id, nome, descricao FROM categorias WHERE id = ?",
                (categoria_id,),
            )
            categoria = build_categoria(cursor.fetchone())
            log_event(ctx, logging.INFO, f"categoria atualizada id={categoria_id}")
            return categoria
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            log_event(ctx, logging.ERROR, f"falha ao atualizar categoria id={categoria_id}: {exc}")
            raise Fault(faultcode="Client.Data", faultstring="Nome de categoria ja utilizado.") from exc
        finally:
            conn.close()

    @rpc(Integer, _in_header=(SecurityHeader,), _returns=ResultadoOperacao)
    def remover_categoria(ctx, categoria_id):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cursos WHERE categoria_id = ?", (categoria_id,))
        if cursor.fetchone()["total"] > 0:
            conn.close()
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} possui cursos vinculados")
            raise Fault(
                faultcode="Client.Data",
                faultstring="Nao e possivel remover categoria com cursos vinculados.",
            )
        cursor.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        conn.commit()
        removidos = cursor.rowcount
        conn.close()
        if removidos == 0:
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} nao encontrada para remocao")
            raise Fault(faultcode="Client", faultstring="Categoria nao encontrada.")
        log_event(ctx, logging.INFO, f"categoria removida id={categoria_id}")
        return ResultadoOperacao(sucesso="true", mensagem="Categoria removida com sucesso.")

    @rpc(Unicode, Integer, Integer, Integer, _in_header=(SecurityHeader,), _returns=Curso)
    def cadastrar_curso(ctx, nome, categoria_id, carga_horaria, preco):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorias WHERE id = ?", (categoria_id,))
        if cursor.fetchone() is None:
            conn.close()
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} inexistente no cadastro de curso")
            raise Fault(faultcode="Client.Data", faultstring="Categoria informada nao existe.")
        cursor.execute(
            """
            INSERT INTO cursos (nome, categoria_id, carga_horaria, preco)
            VALUES (?, ?, ?, ?)
            """,
            (nome, categoria_id, carga_horaria, preco),
        )
        conn.commit()
        curso_id = cursor.lastrowid
        cursor.execute(
            """
            SELECT c.id, c.nome, c.categoria_id, cat.nome AS categoria_nome,
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
            """,
            (curso_id,),
        )
        curso = build_curso(cursor.fetchone())
        conn.close()
        log_event(ctx, logging.INFO, f"curso criado id={curso_id}")
        return curso

    @rpc(Integer, Unicode, Integer, Integer, Integer, _in_header=(SecurityHeader,), _returns=Curso)
    def atualizar_curso(ctx, curso_id, nome, categoria_id, carga_horaria, preco):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cursos WHERE id = ?", (curso_id,))
        if cursor.fetchone() is None:
            conn.close()
            log_event(ctx, logging.WARNING, f"curso_id={curso_id} nao encontrado para atualizacao")
            raise Fault(faultcode="Client", faultstring="Curso nao encontrado.")
        cursor.execute("SELECT id FROM categorias WHERE id = ?", (categoria_id,))
        if cursor.fetchone() is None:
            conn.close()
            log_event(ctx, logging.WARNING, f"categoria_id={categoria_id} inexistente na atualizacao de curso")
            raise Fault(faultcode="Client.Data", faultstring="Categoria informada nao existe.")
        cursor.execute(
            """
            UPDATE cursos
            SET nome = ?, categoria_id = ?, carga_horaria = ?, preco = ?
            WHERE id = ?
            """,
            (nome, categoria_id, carga_horaria, preco, curso_id),
        )
        conn.commit()
        cursor.execute(
            """
            SELECT c.id, c.nome, c.categoria_id, cat.nome AS categoria_nome,
                   c.carga_horaria, c.preco
            FROM cursos c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
            """,
            (curso_id,),
        )
        curso = build_curso(cursor.fetchone())
        conn.close()
        log_event(ctx, logging.INFO, f"curso atualizado id={curso_id}")
        return curso

    @rpc(Integer, _in_header=(SecurityHeader,), _returns=ResultadoOperacao)
    def remover_curso(ctx, curso_id):
        require_authentication(ctx)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cursos WHERE id = ?", (curso_id,))
        conn.commit()
        removidos = cursor.rowcount
        conn.close()
        if removidos == 0:
            log_event(ctx, logging.WARNING, f"curso_id={curso_id} nao encontrado para remocao")
            raise Fault(faultcode="Client", faultstring="Curso nao encontrado.")
        log_event(ctx, logging.INFO, f"curso removido id={curso_id}")
        return ResultadoOperacao(sucesso="true", mensagem="Curso removido com sucesso.")

    @rpc(Unicode, Unicode, Unicode, _returns=Administrador)
    def criar_administrador(ctx, usuario, senha, nome):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO administradores (usuario, senha, nome) VALUES (?, ?, ?)",
                (usuario, senha_hash.decode("utf-8"), nome),
            )
            conn.commit()
            admin_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, usuario, nome, criado_em FROM administradores WHERE id = ?",
                (admin_id,),
            )
            row = cursor.fetchone()
            log_event(ctx, logging.INFO, f"administrador criado id={admin_id}")
            return Administrador(
                id=row["id"],
                usuario=row["usuario"],
                nome=row["nome"],
                criado_em=row["criado_em"],
            )
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            log_event(ctx, logging.ERROR, f"falha ao criar administrador usuario={usuario}: {exc}")
            raise Fault(faultcode="Client.Data", faultstring="Usuario ja cadastrado.") from exc
        finally:
            conn.close()

    @rpc(Unicode, Unicode, _returns=Token)
    def login(ctx, usuario, senha):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, usuario, senha, nome FROM administradores WHERE usuario = ?",
            (usuario,),
        )
        row = cursor.fetchone()
        conn.close()
        if row is None or not bcrypt.checkpw(senha.encode("utf-8"), row["senha"].encode("utf-8")):
            log_event(ctx, logging.WARNING, f"falha de autenticacao usuario={usuario}")
            raise Fault(faultcode="Client.Auth", faultstring="Usuario ou senha invalidos.")
        token, expira_em = generate_token(row)
        log_event(ctx, logging.INFO, f"login realizado usuario={usuario}")
        return Token(
            token=token,
            tipo="Bearer",
            expira_em=expira_em,
            administrador_id=row["id"],
            administrador_nome=row["nome"],
        )

    @rpc(_in_header=(SecurityHeader,), _returns=Unicode)
    def validar_token(ctx):
        payload = require_authentication(ctx)
        return f"Token valido para o usuario {payload.get('usuario')}."


application = Application(
    [CatalogoCursosService],
    tns=TNS,
    name="CatalogoCursosService",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

base_wsgi_app = WsgiApplication(application)


def soap_fault(start_response, message, status="500 Internal Server Error"):
    body = f"""<?xml version='1.0' encoding='UTF-8'?>
<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap11env:Body>
    <soap11env:Fault>
      <faultcode>Client.Auth</faultcode>
      <faultstring>{message}</faultstring>
    </soap11env:Fault>
  </soap11env:Body>
</soap11env:Envelope>""".encode("utf-8")
    start_response(status, [("Content-Type", "text/xml; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


class JwtSecurityMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get("REQUEST_METHOD") != "POST":
            return self.app(environ, start_response)

        try:
            content_length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError:
            content_length = 0

        body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
        environ["wsgi.input"] = io.BytesIO(body)

        try:
            envelope = etree.fromstring(body)
        except Exception:
            return self.app(environ, start_response)

        ns = {"soap": SOAP_ENV_NS, "wsse": WSSE_NS}
        operation = envelope.find("soap:Body/*", namespaces=ns)
        if operation is None:
            return self.app(environ, start_response)

        operation_name_value = etree.QName(operation.tag).localname
        if operation_name_value not in PROTECTED_OPERATIONS:
            return self.app(environ, start_response)

        header_token = envelope.findtext("soap:Header/wsse:Security/wsse:BinarySecurityToken", namespaces=ns)
        if not header_token:
            # Backward-compatible custom header support.
            header_token = envelope.findtext(
                "soap:Header/{http://exemplo.com/catalogocursos}SecurityHeader/{http://exemplo.com/catalogocursos}token",
                namespaces=ns,
            )
        if not header_token:
            logger.warning("[%s] ip=%s cabecalho SOAP ausente", operation_name_value, environ.get("REMOTE_ADDR", "desconhecido"))
            return soap_fault(
                start_response,
                "Cabecalho SOAP de seguranca ausente. Informe wsse:Security/wsse:BinarySecurityToken.",
            )

        try:
            payload = decode_token(header_token)
            logger.info(
                "[%s] ip=%s autenticado via middleware usuario=%s",
                operation_name_value,
                environ.get("REMOTE_ADDR", "desconhecido"),
                payload.get("usuario"),
            )
        except Fault as fault:
            logger.warning("[%s] ip=%s falha JWT: %s", operation_name_value, environ.get("REMOTE_ADDR", "desconhecido"), fault.faultstring)
            return soap_fault(start_response, fault.faultstring)

        environ["HTTP_X_AUTHENTICATED_PAYLOAD"] = header_token
        return self.app(environ, start_response)


wsgi_app = JwtSecurityMiddleware(base_wsgi_app)


if __name__ == "__main__":
    print(f"Servidor rodando em http://127.0.0.1:{PORT}")
    print(f"WSDL disponivel em http://127.0.0.1:{PORT}/?wsdl")
    print(f"Logs disponiveis em {LOG_PATH}")
    try:
        from waitress import serve

        serve(wsgi_app, host="127.0.0.1", port=PORT)
    except ImportError:
        class QuietHandler(WSGIRequestHandler):
            # Force HTTP/1.0 responses to avoid client hangs caused by keep-alive handling.
            protocol_version = "HTTP/1.0"

        httpd = make_server("127.0.0.1", PORT, wsgi_app, handler_class=QuietHandler)
        httpd.serve_forever()
