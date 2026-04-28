# Evidencias para SoapUI e Postman

## WSDL

- URL local: `http://127.0.0.1:8010/?wsdl`
- Arquivo exportado: `docs/contratos/catalogo_cursos.wsdl`
- XSD exportado: `docs/contratos/catalogo_cursos.xsd`

## Header SOAP de seguranca

As operacoes de escrita exigem o header abaixo:

```xml
<soapenv:Header>
   <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
   </wsse:Security>
</soapenv:Header>
```

Namespace:

```text
xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
```

## Testes recomendados no SoapUI

1. Importar o WSDL local.
2. Executar `listar_cursos` sem header para validar acesso publico.
3. Executar `login` com `admin` / `admin123`.
4. Copiar o JWT retornado.
5. Executar `cadastrar_categoria` com o header `wsse:Security`.
6. Executar `atualizar_categoria`, `cadastrar_curso`, `atualizar_curso`, `remover_curso` e `remover_categoria`.
7. Executar cenarios de erro:
   - sem `wsse:Security`
   - token invalido
   - token expirado
   - XML malformado
   - categoria inexistente
   - remocao de categoria com cursos vinculados

## Exemplo de login

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

## Exemplo de operacao protegida

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cat="http://exemplo.com/catalogocursos">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
         <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <cat:cadastrar_categoria>
         <cat:nome>Mobile</cat:nome>
         <cat:descricao>Desenvolvimento de aplicativos moveis</cat:descricao>
      </cat:cadastrar_categoria>
   </soapenv:Body>
</soapenv:Envelope>
```
