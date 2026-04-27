
# Catálogo de Cursos - Web Service SOAP

## Requisitos

- Python 3.8+
- VS Code (opcional)
- Biblioteca bcrypt (para hash de senhas)

## Instalação

1. Crie um ambiente virtual (opcional):
   python -m venv venv

2. Ative o ambiente:
   Windows: venv\Scripts\activate
   Mac/Linux: source venv/bin/activate

3. Instale as dependências:
   pip install -r requirements.txt

## Configuração do Banco de Dados

Este projeto utiliza SQLite como banco de dados para persistência dos cursos.

1. **Inicializar o banco de dados** (cria o arquivo `cursos.db` e insere dados iniciais):
   ```bash
   python init_db.py
   ```

   O script criará automaticamente:
   - O arquivo de banco de dados `cursos.db`
   - A tabela `cursos` com as colunas: id, nome, categoria, carga_horaria, preco
   - 3 cursos de exemplo

    2. **Estrutura do banco de dados**:
    ```sql
    CREATE TABLE administradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        nome TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    
    CREATE TABLE categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT
    )
    
    CREATE TABLE cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria_id INTEGER NOT NULL,
        carga_horaria INTEGER NOT NULL,
        preco INTEGER NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )
    ```

## Executando o Serviço

1. Certifique-se de que o banco de dados foi inicializado:
   ```bash
   python init_db.py
   ```

2. Inicie o servidor:
   ```bash
   python app.py
   ```

O serviço ficará disponível em:
http://localhost:8000

WSDL:
http://localhost:8000/?wsdl

## Operações Disponíveis

### Autenticação
- **criar_administrador(usuario, senha, nome)** - Cria um novo administrador
- **login(usuario, senha)** - Realiza login e retorna um token de autenticação
- **validar_token(token)** - Valida se um token é válido
- **logout(token)** - Invalida um token de autenticação

### Cursos
- **listar_cursos()** - Retorna todos os cursos do banco de dados
- **consultar_curso(curso_id)** - Consulta um curso específico pelo ID
- **buscar_por_categoria(categoria)** - Busca cursos por categoria (case-insensitive)
- **cadastrar_curso(nome, categoria_id, carga_horaria, preco)** - Cadastra um novo curso vinculado a uma categoria

### Categorias
- **listar_categorias()** - Retorna todas as categorias disponíveis
- **cadastrar_categoria(nome, descricao)** - Cadastra uma nova categoria

## Exemplos de Uso

### Criar um novo administrador
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:criar_administrador>
         <cat:usuario>joao</cat:usuario>
         <cat:senha>senha123</cat:senha>
         <cat:nome>João Silva</cat:nome>
      </cat:criar_administrador>
   </soapenv:Body>
</soapenv:Envelope>
```

### Login (obter token)
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:login>
         <cat:usuario>admin</cat:usuario>
         <cat:senha>admin123</cat:senha>
      </cat:login>
   </soapenv:Body>
</soapenv:Envelope>
```

### Validar token
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:validar_token>
         <cat:token>seu_token_aqui</cat:token>
      </cat:validar_token>
   </soapenv:Body>
</soapenv:Envelope>
```

### Logout
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:logout>
         <cat:token>seu_token_aqui</cat:token>
      </cat:logout>
   </soapenv:Body>
</soapenv:Envelope>
```

### Cadastrar uma nova categoria
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:cadastrar_categoria>
         <cat:nome>Mobile</cat:nome>
         <cat:descricao>Desenvolvimento de aplicativos móveis</cat:descricao>
      </cat:cadastrar_categoria>
   </soapenv:Body>
</soapenv:Envelope>
```

### Cadastrar um novo curso
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:cadastrar_curso>
         <cat:nome>React Native</cat:nome>
         <cat:categoria_id>4</cat:categoria_id>
         <cat:carga_horaria>45</cat:carga_horaria>
         <cat:preco>400</cat:preco>
      </cat:cadastrar_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## Testando o Serviço

Você pode testar usando:
- **SoapUI** - Importe o WSDL: http://localhost:8000/?wsdl
- **Postman** - Configure requisições SOAP usando o endpoint
- **Navegador** - Acesse http://localhost:8000/?wsdl para ver a definição do serviço

## Dados Iniciais

### Administrador
O banco de dados é inicializado com 1 administrador padrão:

- **Usuário:** admin
- **Senha:** admin123
- **Nome:** Administrador Padrão

⚠️ **Importante:** Altere a senha do administrador padrão após o primeiro acesso.

### Categorias
O banco de dados é inicializado com 3 categorias de exemplo:

1. Programação - Cursos de linguagens de programação
2. Web - Desenvolvimento web front-end e back-end
3. Dados - Banco de dados e análise de dados

### Cursos
O banco de dados é inicializado com 3 cursos vinculados às categorias:

1. Python Básico (Categoria: Programação) - 40h - R$ 200
2. Desenvolvimento Web (Categoria: Web) - 60h - R$ 350
3. Banco de Dados (Categoria: Dados) - 50h - R$ 300

## Gerenciando o Banco de Dados

Você pode gerenciar o banco de dados diretamente usando ferramentas como:
- **DB Browser for SQLite** - Interface gráfica gratuita
- **sqlite3** (linha de comando):
  ```bash
  sqlite3 cursos.db
  ```

Exemplos de comandos SQL:
```sql
-- Listar todos os administradores
SELECT id, usuario, nome, criado_em FROM administradores;

-- Listar todas as categorias
SELECT * FROM categorias;

-- Listar todos os cursos com nome da categoria
SELECT c.id, c.nome, cat.nome as categoria, c.carga_horaria, c.preco
FROM cursos c
LEFT JOIN categorias cat ON c.categoria_id = cat.id;

-- Adicionar uma nova categoria
INSERT INTO categorias (nome, descricao) 
VALUES ('Mobile', 'Desenvolvimento de aplicativos móveis');

-- Adicionar um novo curso vinculado a uma categoria
INSERT INTO cursos (nome, categoria_id, carga_horaria, preco) 
VALUES ('React Native', 4, 45, 400);

-- Buscar cursos por categoria
SELECT c.*, cat.nome as categoria_nome
FROM cursos c
LEFT JOIN categorias cat ON c.categoria_id = cat.id
WHERE cat.nome = 'Programação';
```
