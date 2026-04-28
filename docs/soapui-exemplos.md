# Exemplos SoapUI e Postman

Este documento apresenta exemplos completos de requisicoes SOAP para uso no SoapUI ou Postman.

Padrao comum a todos os testes:

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`

Header SOAP WS-Security usado nas operacoes protegidas:

```xml
<soapenv:Header>
   <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
   </wsse:Security>
</soapenv:Header>
```

## 1. Login

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: retorno de token JWT em `loginResponse`

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

## 2. Listar cursos

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: lista de cursos em `listar_cursosResponse`

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:listar_cursos/>
   </soapenv:Body>
</soapenv:Envelope>
```

## 3. Consultar curso

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: retorno de um curso especifico ou erro se o id nao existir

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:consultar_curso>
         <cat:curso_id>2</cat:curso_id>
      </cat:consultar_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## 4. Cadastrar curso com WS-Security

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: criacao de curso e retorno em `cadastrar_cursoResponse`

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:cadastrar_curso>
         <cat:nome>Curso de Teste SOAP</cat:nome>
         <cat:categoria_id>2</cat:categoria_id>
         <cat:carga_horaria>40</cat:carga_horaria>
         <cat:preco>199</cat:preco>
      </cat:cadastrar_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## 5. Atualizar curso com WS-Security

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: atualizacao do curso e retorno em `atualizar_cursoResponse`

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:atualizar_curso>
         <cat:curso_id>2</cat:curso_id>
         <cat:nome>Desenvolvimento Web Atualizado</cat:nome>
         <cat:categoria_id>2</cat:categoria_id>
         <cat:carga_horaria>72</cat:carga_horaria>
         <cat:preco>420</cat:preco>
      </cat:atualizar_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## 6. Remover curso com WS-Security

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: retorno de `ResultadoOperacao` com remocao bem-sucedida

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:remover_curso>
         <cat:curso_id>5</cat:curso_id>
      </cat:remover_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## 7. Requisicao sem token

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: `SOAP Fault` informando ausencia de header de seguranca

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:cadastrar_curso>
         <cat:nome>Curso Sem Token</cat:nome>
         <cat:categoria_id>2</cat:categoria_id>
         <cat:carga_horaria>20</cat:carga_horaria>
         <cat:preco>99</cat:preco>
      </cat:cadastrar_curso>
   </soapenv:Body>
</soapenv:Envelope>
```

## 8. Requisicao com token invalido

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: `SOAP Fault` informando token JWT invalido

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>TOKEN_INVALIDO</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:validar_token/>
   </soapenv:Body>
</soapenv:Envelope>
```

## 9. Exemplo de XML malformado

- URL: `http://127.0.0.1:8010`
- Metodo: `POST`
- Header HTTP: `Content-Type: text/xml; charset=utf-8`
- Resultado esperado: erro de parse XML ou `SOAP Fault`, conforme o cliente utilizado

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:listar_cursos>
   </soapenv:Body>
</soapenv:Envelope>
```

## Observacoes de uso

- Execute primeiro o `login` para obter um JWT valido.
- Substitua `JWT_OBTIDO_NO_LOGIN` pelo token retornado pelo servico.
- Para testes de remocao e atualizacao, ajuste os ids conforme os registros existentes no banco SQLite.
- O WSDL para importacao no SoapUI esta disponivel em `http://127.0.0.1:8010/?wsdl`.
