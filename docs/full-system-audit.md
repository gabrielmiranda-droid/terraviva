# Auditoria tecnica completa do ERP

Data da auditoria: 2026-08-14

Projeto auditado: `papai`

## Resumo executivo

O ERP tem uma base tecnica funcional para cadastro, entrada de maquinas, geracao de OS, consulta de produtos importados e autenticacao. Os testes automatizados atuais passam, o build do frontend passa, e a migration atual esta aplicada no Supabase.

O sistema ainda nao esta pronto para operacao real de venda, financeiro, orcamento e baixa de estoque. Esses modulos possuem telas ou models, mas nao possuem fluxo backend completo, transacoes atomicas, idempotencia, estorno, validacao de saldo ou auditoria de movimentos.

O maior risco tecnico hoje e a duplicidade de fonte de produto/estoque: o frontend consulta `erp.produtos` e `erp.estoque_saldos`, enquanto os models operacionais e o importador SICNET novo escrevem em `public.parts` e `public.stock_movements`. Antes de ativar venda/OS com estoque real, essa decisao precisa ser fechada.

## Arquitetura encontrada

- Frontend React/TypeScript em `frontend/src`.
- Backend FastAPI em `backend/app`.
- ORM SQLAlchemy com migrations Alembic.
- Banco Supabase PostgreSQL.
- Schema `erp` para produtos importados da planilha GELEIA/SIC.
- Schema `public` para ERP operacional.
- Importador SICNET SQL Server em `backend/app/importers/sicnet`.

## Funcionalidades funcionando

| Modulo | Evidencia | Status |
| --- | --- | --- |
| Auth | `POST /auth/login`, `GET /auth/me`, teste backend | Funcionando |
| Dashboard | Endpoints de metricas e fluxo | Funcionando |
| Clientes | Listar, criar, consultar, atualizar | Funcionando parcial |
| Maquinas | Listar, criar, consultar, atualizar | Funcionando parcial |
| Entrada de maquina | Cria entrada e OS em uma transacao | Funcionando parcial |
| Oficina | Lista maquinas nao entregues e marca entrega | Funcionando parcial |
| OS | Lista, detalhe, diagnostico e status | Funcionando parcial |
| Produtos importados | Consulta `erp.*` | Funcionando como leitura |
| Estoque importado | Saldos batem com movimentos iniciais | Funcionando como leitura |
| Importador SICNET | Dry-run executado com status OK | Funcionando em modo analise |

## Funcionalidades parciais

| Modulo | Situacao |
| --- | --- |
| Clientes | Nao normaliza CPF/CNPJ, nao impede documento duplicado, nao ha inativacao dedicada na tela |
| Maquinas | Nao ha historico completo na tela, apenas vinculo com cliente |
| Entrada | Frontend bloqueia durante submit, mas backend nao recebe idempotency key para clique duplo/retry |
| OS | Status aceita qualquer valor do enum, sem mapa de transicoes valido |
| Orcamento | Tela mostra fila de OS aguardando aprovacao, mas nao cria orcamento nem itens |
| Produtos | Consulta importados de `erp.*`; sem edicao ou integracao com `public.parts` |
| Estoque | Indicadores existem; nao ha ajuste, compra, transferencia, baixa ou estorno |
| Impressao | Registra print job e abre impressao do navegador, sem workflow de fila real |

## Funcionalidades quebradas ou nao conectadas

| Modulo | Problema | Gravidade |
| --- | --- | --- |
| Venda balcao | Carrinho e busca existem, mas finalizar venda esta desabilitado e nao ha endpoint de venda | Critico |
| Pagamentos | Model/tabela existem, mas nao ha service/router/tela persistindo pagamento | Critico |
| Baixa de estoque venda | Nao existe fluxo `sale -> sale_items -> payment -> stock_movements` | Critico |
| Baixa de estoque OS | Aba visual existe, mas nao ha endpoint de consumo de peca | Critico |
| Estorno/cancelamento | Nao ha fluxo de cancelamento de venda, OS ou consumo com movimento inverso | Critico |
| Orcamento real | Model existe, mas nao ha criacao/aprovacao/recusa/versionamento via API | Alto |
| Fornecedores | Model e importador existem, sem tela/API operacional | Medio |
| Localizacoes | Model e importador existem, sem tela/API operacional | Medio |

## Riscos criticos

1. Estoque pode ficar errado se venda/OS forem implementadas em cima da fonte errada.
2. `erp.*` e `public.parts` coexistem sem sincronizacao operacional.
3. Venda nao baixa estoque porque nao existe finalizacao real.
4. OS nao consome pecas porque nao existe endpoint de consumo.
5. Nao existe rollback de venda/pagamento/estoque porque o fluxo nao foi implementado.
6. Nao existe idempotencia para operacoes criticas como entrada, venda futura, consumo e importacao real.
7. Nao foi encontrado mecanismo de concorrencia para impedir dois usuarios venderem a ultima unidade.
8. RLS esta desabilitado em `public.*`; se o app depender de acesso direto via Supabase client no futuro, ha risco de exposicao.

## Estoque

O estoque real disponivel hoje para consulta esta em `erp.estoque_saldos`. Ele esta consistente com `erp.estoque_movimentos`, com 0 divergencias na auditoria.

Dados importantes:

- 10.777 produtos em `erp.produtos`.
- 10.777 saldos em `erp.estoque_saldos`.
- 10.777 movimentos iniciais em `erp.estoque_movimentos`.
- 1.126 itens com estoque negativo.
- 5.111 itens zerados.
- 16 produtos sem preco ou preco zero.
- 120 grupos de SKU duplicado.

`public.parts` esta vazio, entao o ERP operacional ainda nao tem produto/estoque proprio carregado.

## Venda

Venda balcao nao esta pronta para uso real. A tela busca produto em `/erp-products`, adiciona itens em um carrinho local e calcula total no frontend, mas o botao `Finalizar venda` esta desabilitado. Nao ha endpoints para:

- criar venda;
- adicionar itens;
- recalcular total no backend;
- registrar pagamento;
- baixar estoque;
- cancelar venda;
- estornar estoque;
- emitir ou marcar nota fiscal solicitada.

Conclusao: nao existe risco atual de baixar estoque errado pela venda porque a venda nao executa. O risco aparece ao ativar esse modulo sem definir transacao e fonte de estoque.

## OS

A entrada cria uma OS automaticamente. Isso funciona e esta coberto por teste. O detalhe da OS permite alterar status e registrar diagnostico.

Pontos ausentes:

- adicionar peca;
- adicionar servico;
- criar orcamento real;
- aprovar/recusar orcamento;
- consumir peca;
- baixar estoque;
- estornar consumo;
- pagamento de OS;
- mapa de transicao valido.

Status atual: OS operacional basica funciona; OS financeira/estoque ainda nao.

## Orcamento

As tabelas e models existem, mas nao ha endpoint de orcamento. A tela `/orcamentos` e uma fila filtrando OS com status `AGUARDANDO_APROVACAO`.

Regra critica atendida por ausencia: orcamento nao baixa estoque, porque o fluxo nao existe. Porem tambem nao existe aprovacao/recusa real.

## Clientes

Clientes funcionam para criar, listar, buscar, ver detalhe e atualizar via API. Ha auditoria de criacao/alteracao.

Riscos:

- documento nao e normalizado;
- documento duplicado nao e bloqueado;
- documento vazio e aceito;
- nao ha merge/inativacao dedicado;
- importados SICNET podem coexistir com manuais se nao houver estrategia de deduplicacao.

## Produtos

Produtos visiveis no frontend sao produtos do schema `erp`, nao `public.parts`.

Riscos encontrados:

- `erp` tem 120 grupos de SKU duplicado.
- `erp` tem 258 grupos de descricao duplicada.
- `erp` tem 16 produtos sem preco ou preco zero.
- `public.parts` possui constraint de `internal_code` unico, e o importador ja trata duplicidade de codigos internos do SICNET removendo o valor duplicado do campo unico.

## Fornecedores

`public.suppliers` existe e o importador SICNET prepara carga, mas a tabela esta vazia no Supabase atual e nao ha endpoint/tela operacional.

## Localizacoes

`public.product_locations` existe e o importador SICNET prepara carga. O schema `erp` tem `locais_estoque` com 1 local. Ainda nao ha tela/API para manutencao de localizacao operacional.

## Pagamentos

`public.payments` existe, mas nao ha router/service. Nao foi possivel validar pagamento parcial, cancelamento, estorno, duplicidade ou vinculo com venda/OS.

## Nota fiscal solicitada

Nao foi encontrada implementacao operacional de nota fiscal solicitada em venda. Nao ha checkbox persistido, status fiscal, filtro ou workflow fiscal.

## Supabase e seguranca

Achados:

- Conexao com `DATABASE_URL` OK.
- Alembic em `0004_sicnet_migration_support`.
- `erp.*` com RLS habilitado.
- `public.*` com RLS desabilitado.
- Nenhuma policy retornada por `pg_policies` para `public` ou `erp`.
- Backend usa JWT proprio e SQLAlchemy direto; nesse modelo, RLS do Supabase nao protege o acesso feito pelo backend.
- Nao ha `company_id`; sistema aparenta ser single-company.

Observacao: como a senha do banco apareceu em captura/arquivo `.env`, recomenda-se trocar a senha no Supabase antes de usar em producao.

## Migrations

As migrations estao ordenadas e o banco remoto esta no head. Nao foram detectadas migrations pendentes pelo Alembic.

Risco: o schema `erp` provavelmente foi criado por SQL/manual/importacao anterior alem do Alembic operacional. Isso precisa permanecer documentado para evitar divergencia entre ambiente novo e ambiente atual.

## Model vs banco

Foi gerado um diff automatico entre `Base.metadata` do SQLAlchemy e o Supabase configurado em `DATABASE_URL`.

Resultado:

- 20 tabelas mapeadas nos models.
- 0 tabelas modeladas ausentes no banco.
- 0 diferencas de colunas/nullability nas tabelas modeladas.
- 8 tabelas extras no banco sem model SQLAlchemy direto, todas do schema `erp`.

Detalhe em `docs/model-db-diff.md`.

## Testes

Executado:

- Backend: `python -m pytest` -> 6 passed, 1 warning.
- Alembic: `python -m alembic current` -> `0004_sicnet_migration_support (head)`.
- Alembic heads: `0004_sicnet_migration_support (head)`.
- Frontend: `npm run build` -> passou, incluindo `tsc -b`.
- SICNET dry-run: passou, relatorio salvo em `docs/sicnet-initial-migration-report.md`.

Nao executado:

- Ruff/lint backend: indisponivel, `No module named ruff`.
- E2E real de venda/OS estoque: nao existe fluxo implementado para exercitar.

## Fechamento literal do prompt

O checklist item a item do prompt esta em `docs/audit-prompt-completion-checklist.md`.

Itens como venda com baixa de estoque, pagamento, cancelamento, estorno, consumo de peca em OS e E2E financeiro/estoque foram classificados como nao testaveis dinamicamente no estado atual, porque nao existem endpoints/servicos reais para executar esses fluxos.

## Codigo morto ou nao usado

| Area | Evidencia |
| --- | --- |
| Models de venda | Tabelas existem, sem endpoint |
| Models de pagamento | Tabela existe, sem endpoint |
| Models de orcamento | Tabelas existem, sem endpoint |
| Models de partes/fornecedores/localizacoes | Existem, mas frontend usa `erp-products` |
| Importador `legacy_sic.py` | Endpoint antigo analisa XLSX; importador novo SICNET SQL Server usa CLI separado |

## Matriz de funcionalidades

| Modulo | Frontend | Backend | Banco | Testado | Status |
| --- | --- | --- | --- | --- | --- |
| Auth | OK | OK | OK | Sim | Funcionando |
| Dashboard | OK | OK | OK | Parcial | Funcionando |
| Clientes | OK | OK | OK | Sim | Funcionando parcial |
| Maquinas | OK | OK | OK | Sim | Funcionando parcial |
| Entrada | OK | OK | OK | Sim | Funcionando parcial |
| Oficina/entrega | OK | OK | OK | Parcial | Funcionando parcial |
| OS status | OK | OK | OK | Parcial | Parcial |
| Orcamento | Parcial | Nao | Tabela existe | Nao | Nao conectado |
| Produtos | OK leitura | OK leitura | OK em `erp` | Parcial | Consulta funcionando |
| Estoque | Parcial | Parcial leitura | OK em `erp` | Sim leitura | Risco arquitetural |
| Venda balcao | Mock/parcial | Nao | Tabela vazia | Nao | Nao conectado |
| Pagamentos | Nao | Nao | Tabela vazia | Nao | Nao conectado |
| Fornecedores | Nao | Nao | Tabela vazia | Nao | Nao conectado |
| Localizacoes | Nao | Nao | Tabela vazia | Nao | Nao conectado |
| Importador SICNET | Nao | CLI | Estrutura OK | Dry-run | Pronto para proxima revisao |

## Recomendacoes

1. Definir a fonte unica de produtos/estoque antes de desenvolver venda e OS com pecas.
2. Criar service transacional de estoque antes dos endpoints de venda/consumo.
3. Implementar idempotencia para entrada, venda, consumo, estorno e importacao real.
4. Implementar mapa de transicoes validas de OS.
5. Criar endpoints reais para orcamento antes de evoluir a tela.
6. Criar venda balcao com recalculo de total no backend e baixa atomica apenas na finalizacao.
7. Criar cancelamento/estorno por movimento inverso, nunca apagando historico.
8. Revisar RLS/policies se o frontend algum dia acessar Supabase diretamente.
