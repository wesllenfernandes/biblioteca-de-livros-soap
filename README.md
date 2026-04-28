# Catalogo de Cursos SOAP

Servico SOAP para catalogo de cursos com persistencia em SQLite, contrato WSDL/XSD, autenticacao JWT em header SOAP com formato WS-Security, CRUD basico e logs de execucao.

## Requisitos

- Python 3.10+
- Dependencias de `requirements.txt`

Observacao:

- Para resposta HTTP mais estavel no Windows, instale todas as dependencias, incluindo `waitress`.

## Instalcao e execucao

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Endpoints locais:

- Servico SOAP: `http://127.0.0.1:8010`
- WSDL: `http://127.0.0.1:8010/?wsdl`

## Requisitos da atividade atendidos

### 1. Contrato formal

- O servico e integralmente SOAP 1.1 com WSDL gerado em `/?wsdl`.
- Os tipos sao expostos em XML Schema dentro do contrato.
- O script `export_contracts.py` salva evidencias locais em `docs/contratos/`.

### 2. CRUD com banco de dados

Operacoes publicas:

- `listar_cursos`
- `consultar_curso`
- `buscar_por_categoria`
- `listar_categorias`
- `consultar_categoria`
- `login`
- `criar_administrador`

Operacoes protegidas por JWT em header SOAP:

- `cadastrar_categoria`
- `atualizar_categoria`
- `remover_categoria`
- `cadastrar_curso`
- `atualizar_curso`
- `remover_curso`
- `validar_token`

### 3. Seguranca SOAP

- Autenticacao baseada em JWT.
- Token enviado em header SOAP padrao `wsse:Security/wsse:BinarySecurityToken`.
- Falhas de autenticacao retornam `SOAP Fault`.
- Pelo menos uma operacao protegida: todas as operacoes de escrita exigem token.

Header esperado:

```xml
<soapenv:Header>
   <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
   </wsse:Security>
</soapenv:Header>
```

Exemplo completo de requisicao protegida:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:validar_token/>
   </soapenv:Body>
</soapenv:Envelope>
```

### 4. Monitoramento e logs

- Logs em arquivo: `logs/catalogo_soap.log`
- Registra chamadas relevantes, autenticacao, erros de negocio e tentativas invalidas.

## Fluxo de teste no SoapUI

1. Abrir o WSDL `http://127.0.0.1:8010/?wsdl`.
2. Executar `login` com `admin` e `admin123`.
3. Copiar o JWT retornado.
4. Inserir o token no header SOAP.
5. Testar CRUD de categoria e curso.
6. Testar erros:
   - sem header
   - token invalido
   - XML malformado
   - categoria inexistente
   - remocao de categoria com cursos vinculados

Exemplos prontos: [docs/soapui-exemplos.md](/c:/Users/wesll/Downloads/SISTEMAS%20PARA%20INTERNET/ORIETADO%20A%20SERVI%C3%87OS/projeto%20orietado%20a%20servi%C3%A7o/catalogo_cursos_soap/docs/soapui-exemplos.md)

## Exportar WSDL e XSD

Com o servidor em execucao:

```bash
python export_contracts.py
```

Arquivos gerados:

- `docs/contratos/catalogo_cursos.wsdl`
- `docs/contratos/catalogo_cursos.xsd`

## Dados iniciais

Administrador padrao:

- usuario: `admin`
- senha: `admin123`

Categorias iniciais:

- Programacao
- Web
- Dados

## Observacoes para o relatorio

- A seguranca adotada foi JWT em header SOAP com estrutura `wsse:Security`, por ser simples de demonstrar em ambiente academico, interoperavel com clientes heterogeneos e suficiente para proteger operacoes sensiveis sem abandonar o contrato SOAP.
- A validacao estrutural das mensagens ocorre no protocolo SOAP com `validator="lxml"`, o que ajuda nos testes de XML malformado.
- O WSDL e o XSD podem ser importados no SoapUI como evidencia formal do contrato.
- Evidencias e checklist final da entrega estao em `docs/evidencias.md`.
