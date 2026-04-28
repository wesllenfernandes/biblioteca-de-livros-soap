# Evidencias da Unidade 3

Este documento consolida as evidencias tecnicas do servico SOAP `CatalogoCursosService`, cobrindo contrato formal, XML Schema, seguranca, testes, logs e itens que devem ser capturados manualmente no SoapUI/Postman e no navegador.

## 1. Evidencia do WSDL

- URL do WSDL: `http://127.0.0.1:8010/?wsdl`
- Arquivo salvo no projeto: `docs/contratos/catalogo_cursos.wsdl`
- Endpoint principal do servico: `http://127.0.0.1:8010`

O arquivo WSDL descreve o contrato SOAP 1.1 do servico, incluindo:

- operacoes publicas e protegidas do catalogo de cursos;
- mensagens de entrada e saida de cada operacao;
- binding SOAP document/literal;
- referencia ao arquivo XSD externo `catalogo_cursos.xsd` por meio de `xs:include`.

As operacoes visiveis no contrato incluem, entre outras:

- `login`
- `listar_cursos`
- `consultar_curso`
- `buscar_por_categoria`
- `listar_categorias`
- `consultar_categoria`
- `cadastrar_curso`
- `atualizar_curso`
- `remover_curso`
- `cadastrar_categoria`
- `atualizar_categoria`
- `remover_categoria`
- `validar_token`

## 2. Evidencia do XSD

- Arquivo do schema: `docs/contratos/catalogo_cursos.xsd`
- Namespace do schema: `http://exemplo.com/catalogocursos`

O XSD define os tipos XML utilizados pelo servico SOAP. Entre os principais tipos definidos estao:

- `Curso`
- `Categoria`
- `Administrador`
- `Token`
- `ResultadoOperacao`
- `SecurityHeader`
- `LoginRequest`
- `LoginResponse`
- `CadastrarCursoRequest`
- `CadastrarCursoResponse`
- `AtualizarCursoRequest`
- `AtualizarCursoResponse`
- `RemoverCursoRequest`
- `RemoverCursoResponse`
- `ConsultarCursoRequest`
- `ConsultarCursoResponse`
- `ListarCursosResponse`
- `ConsultarCategoriaRequest`
- `ConsultarCategoriaResponse`
- `CadastrarCategoriaRequest`
- `AtualizarCategoriaRequest`
- `RemoverCategoriaRequest`

Padronizacao aplicada no schema:

- `id`, `curso_id`, `categoria_id`, `carga_horaria`: `xs:int`
- `nome`, `descricao`, `usuario`, `senha`, `mensagem`, `token`: `xs:string`
- `preco`: `xs:decimal`
- `sucesso`: `xs:boolean`

O XSD foi mantido com o mesmo `targetNamespace` do WSDL, garantindo coerencia contratual.

## 3. Evidencia de CRUD

O projeto implementa CRUD de cursos com persistencia em banco SQLite.

Operacoes principais de CRUD de curso:

- `cadastrar_curso`
- `listar_cursos`
- `consultar_curso`
- `atualizar_curso`
- `remover_curso`

Operacoes auxiliares de categoria:

- `cadastrar_categoria`
- `listar_categorias`
- `consultar_categoria`
- `atualizar_categoria`
- `remover_categoria`

As operacoes utilizam o banco SQLite local `cursos.db`, com acesso realizado pelo servico SOAP em `app.py`.

## 4. Evidencia de seguranca

O servico utiliza autenticacao JWT transportada em header SOAP no formato compativel com WS-Security.

Estrutura esperada do header:

```xml
<soapenv:Header>
  <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <wsse:BinarySecurityToken>TOKEN_AQUI</wsse:BinarySecurityToken>
  </wsse:Security>
</soapenv:Header>
```

Comportamento esperado:

- operacoes publicas podem ser executadas sem token, como `login` e `listar_cursos`;
- operacoes de escrita exigem token JWT valido;
- ausencia de token gera `SOAP Fault`;
- token invalido gera `SOAP Fault`;
- token valido libera a execucao da operacao protegida.

Operacoes protegidas por token:

- `cadastrar_categoria`
- `atualizar_categoria`
- `remover_categoria`
- `cadastrar_curso`
- `atualizar_curso`
- `remover_curso`
- `validar_token`

## 5. Evidencia de testes

Testes funcionais registrados para o servico:

- `login` com sucesso, retornando JWT;
- `listar_cursos` sem token, com retorno valido;
- `cadastrar_curso` com token valido;
- `atualizar_curso` com token valido;
- `remover_curso` com token valido;
- requisicao sem token, retornando erro de autenticacao;
- token invalido, retornando erro de autenticacao;
- XML malformado, para validar comportamento do parser SOAP/XML.

Resumo dos cenarios:

- sucesso publico: `login`, `listar_cursos`;
- sucesso protegido: `validar_token` e operacoes de escrita com JWT valido;
- falha esperada: sem token, token invalido e XML malformado.

## 6. Evidencia de logs

- Arquivo de log: `logs/catalogo_soap.log`

O sistema registra eventos relevantes de execucao, incluindo:

- inicializacao do servico;
- requisicoes ao endpoint SOAP;
- acesso ao WSDL;
- autenticacao com sucesso;
- erros de autenticacao;
- erros de negocio e erros de execucao.

Tipos de evidencia presentes no log:

- chamada de `login` com sucesso;
- falha de autenticacao;
- chamada protegida autenticada via middleware;
- acesso HTTP ao `/?wsdl`.

Esses registros ajudam a demonstrar monitoramento e rastreabilidade das operacoes do servico.

## 7. Prints recomendados para anexar

Capturas que devem ser geradas manualmente para a entrega:

- print do WSDL aberto no navegador em `http://127.0.0.1:8010/?wsdl`
- print do SoapUI importando o WSDL
- print do `login` retornando token JWT
- print de operacao protegida com token valido
- print de erro sem token
- print de erro com token invalido
- print de exemplo de XML malformado
- print do arquivo `logs/catalogo_soap.log` aberto com registros relevantes

## 8. Conclusao

O projeto apresenta:

- contrato formal via WSDL;
- tipos XML definidos em XSD externo;
- seguranca SOAP com JWT em `wsse:Security/wsse:BinarySecurityToken`;
- testes de sucesso e erro;
- logs de execucao e autenticacao.

As evidencias finais que ainda dependem do aluno sao exclusivamente visuais, por meio de capturas de tela do navegador, SoapUI/Postman e arquivo de log.
