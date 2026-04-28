# Evidencias e Checklist da Entrega

Este arquivo consolida os requisitos da atividade, o que ja esta implementado no projeto e quais evidencias devem ser capturadas no SoapUI/Postman para a entrega final.

## 1. Objetivo do Trabalho

Atendido no projeto:

- Contratos formais bem definidos via WSDL/XSD.
- Seguranca aplicada a servicos SOAP.
- Testes de mensagens SOAP suportados pelo servico.
- Monitoramento e registros de execucao por logs.

## 2. Extensao do Servico Anterior

Atendido no projeto:

- Mesmo dominio de negocio: catalogo de cursos.
- Operacoes do dominio preservadas e evoluidas com autenticacao, logs e validacao.
- Arquitetura orientada a contratos mantida via SOAP, WSDL e XSD.

## 3. Requisito 4.1 Implementacao do Servico SOAP

Atendido no projeto:

- Servico integralmente baseado em SOAP 1.1.
- Operacoes expostas via WSDL.
- Tipos definidos em XML Schema.
- Evolucao do servico sem alterar o dominio de negocio.
- CRUD basico com SQLite para categorias e cursos.

Arquivos de apoio:

- WSDL:
[catalogo_cursos.wsdl](/c:/Users/wesll/Downloads/SISTEMAS%20PARA%20INTERNET/ORIETADO%20A%20SERVI%C3%87OS/projeto%20orietado%20a%20servi%C3%A7o/catalogo_cursos_soap/docs/contratos/catalogo_cursos.wsdl)
- XSD:
[catalogo_cursos.xsd](/c:/Users/wesll/Downloads/SISTEMAS%20PARA%20INTERNET/ORIETADO%20A%20SERVI%C3%87OS/projeto%20orietado%20a%20servi%C3%A7o/catalogo_cursos_soap/docs/contratos/catalogo_cursos.xsd)

## 4. Requisito 4.2 Documentacao do Servico

Atendido no projeto:

- Arquivo WSDL entregue.
- Arquivo XSD entregue.
- Link local do WSDL disponivel em `http://127.0.0.1:8010/?wsdl`.
- Script de exportacao dos contratos em `export_contracts.py`.

Evidencias recomendadas para anexar:

- Print do WSDL aberto no navegador.
- Print do WSDL importado no SoapUI.
- Print das operacoes exibidas no SoapUI.

## 5. Requisito 4.3 Seguranca em Servicos SOAP

Atendido no projeto:

- Seguranca via header SOAP compativel com WS-Security.
- Header utilizado: `wsse:Security`.
- Token utilizado: JWT em `wsse:BinarySecurityToken`.
- Operacoes protegidas por autenticacao:
  - `cadastrar_categoria`
  - `atualizar_categoria`
  - `remover_categoria`
  - `cadastrar_curso`
  - `atualizar_curso`
  - `remover_curso`
  - `validar_token`

Exemplo de header:

```xml
<soapenv:Header>
   <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:BinarySecurityToken>JWT_OBTIDO_NO_LOGIN</wsse:BinarySecurityToken>
   </wsse:Security>
</soapenv:Header>
```

Observacao para o relatorio:

- A implementacao utiliza header SOAP no formato `wsse:Security` para transporte de JWT. Nao inclui assinatura XML nem criptografia da mensagem.

## 6. Requisito 4.4 Testes do Servico SOAP

Atendido tecnicamente no projeto:

- Testes funcionais das operacoes SOAP.
- Validacao estrutural de XML com `Soap11(validator="lxml")`.
- Testes de erro suportados pelo servico:
  - XML malformado
  - ausencia de header de seguranca
  - token invalido
  - token expirado
  - erros de negocio

Checklist minimo de evidencias para anexar:

1. `login` com sucesso.
2. `listar_cursos` com sucesso.
3. `cadastrar_categoria` com token valido.
4. Requisicao sem `wsse:Security`.
5. Requisicao com token invalido.
6. XML malformado.

Ferramentas aceitas:

- SoapUI como principal.
- Postman pode ser usado como apoio.

## 7. Requisito 4.5 Monitoramento e Logs

Atendido no projeto:

- Logs em arquivo: [catalogo_soap.log](/c:/Users/wesll/Downloads/SISTEMAS%20PARA%20INTERNET/ORIETADO%20A%20SERVI%C3%87OS/projeto%20orietado%20a%20servi%C3%A7o/catalogo_cursos_soap/logs/catalogo_soap.log)
- Registro de chamadas, autenticacao e erros.
- Eventos relevantes registrados durante execucao.

Trechos que podem ser usados como evidencia:

```text
2026-04-27 21:53:56,393 [INFO] [login] ip=127.0.0.1 login realizado usuario=wesllen
2026-04-27 22:00:26,656 [INFO] [cadastrar_categoria] ip=desconhecido autenticado via middleware usuario=wesllen
2026-04-27 22:00:26,661 [INFO] [cadastrar_categoria] ip=desconhecido categoria criada id=17
2026-04-27 21:52:17,375 [WARNING] [login] ip=127.0.0.1 falha de autenticacao usuario=wesllen
```

Evidencias recomendadas para anexar:

- Print do terminal com o servidor registrando uma operacao com sucesso.
- Print de um erro autenticacao ou token invalido.
- Print do arquivo de log aberto com os registros.

## 8. Status Final

Status do projeto:

- Implementacao tecnica dos requisitos: atendida.
- Contratos WSDL/XSD: atendidos.
- Seguranca SOAP com JWT em `wsse:Security`: atendida.
- Testes SOAP: suportados e documentados.
- Logs e monitoramento: atendidos.

Para a entrega final, faltam apenas as capturas de tela e evidencias visuais produzidas durante os testes no SoapUI/Postman e no arquivo de log.
