# Checklist de fechamento do prompt de auditoria

Data: 2026-08-14

Objetivo: registrar, item por item, o que foi auditado, o que ficou parcial e o que nao pode ser testado porque o fluxo ainda nao existe no ERP.

## Resultado geral

| Area do prompt | Status | Evidencia/observacao |
| --- | --- | --- |
| Ler estrutura atual | Concluido | Arquivos do frontend, backend, migrations, docs e importadores mapeados |
| Identificar stack | Concluido | React/Vite/TS/Tailwind, FastAPI/SQLAlchemy/Alembic, Supabase PostgreSQL |
| Identificar models | Concluido | Models operacionais e `erp` inspecionados |
| Identificar schemas | Concluido | Schemas Pydantic lidos para clientes, maquinas, entradas, OS, dashboard, produtos |
| Identificar migrations | Concluido | Alembic atual em `0004_sicnet_migration_support` |
| Identificar services/repositories | Concluido | Services e repositories principais lidos |
| Identificar rotas | Concluido | Routers FastAPI e rotas React mapeados |
| Identificar componentes/hooks | Concluido | Layout, auth hook, componentes de UI e rotas mapeados |
| Identificar HTTP services | Concluido | Axios em `frontend/src/services/api.ts` e auth service |
| Identificar env/Supabase | Concluido | `.env` usado em modo leitura; conexao Supabase validada |
| Frontend -> Backend | Concluido | Chamadas reais mapeadas por pagina |
| Backend -> Banco | Concluido | Endpoints existentes mapeados ate tabelas |
| Banco/constraints/indices | Concluido | Constraints e indices consultados no Supabase |
| RLS/Supabase | Concluido | RLS lido em `pg_class`; policies consultadas |
| Company ID | Concluido | Nao encontrado `company_id`; arquitetura atual e single-company |
| Model vs DB | Concluido | `docs/model-db-diff.md`; 0 tabelas modeladas ausentes, 0 diferencas de colunas/nullability |
| Testes backend | Concluido | `pytest`: 6 passed |
| Build/typecheck frontend | Concluido | `npm run build`: passou |
| Lint backend | Parcial | `ruff` nao instalado no `.venv` |
| Rodar migrations | Concluido | `alembic current` e `heads`: `0004` head |
| Importador SICNET dry-run | Concluido | Dry-run OK; sem `import-all` real |
| Auditoria de estoque | Concluido | `docs/stock-consistency-report.md` |
| Gerar relatorio final | Concluido | `docs/full-system-audit.md` |
| Gerar plano de correcao | Concluido | `docs/audit-fix-plan.md` |

## Funcionalidades auditadas

| Funcionalidade | Status | Motivo |
| --- | --- | --- |
| Login | Funcionando | Endpoint e frontend conectados; testes existentes passam |
| Dashboard | Funcionando | Endpoints conectados ao banco |
| Clientes listar/criar/ver/editar API | Funcionando parcial | Falta normalizacao/deduplicacao forte e UI de editar/inativar |
| Clientes inativar | Parcial | Campo existe, PATCH permite, mas nao ha acao dedicada no frontend |
| Maquinas listar/criar/editar API | Funcionando parcial | Falta tela dedicada de detalhe/historico |
| Vincular maquina ao cliente | Funcionando | Backend valida cliente existente |
| Entrada cliente -> maquina -> OS | Funcionando parcial | Cria entrada e OS; falta idempotency key |
| Codigo de entrada | Parcial | `number` unico existe; nao ha endpoint de busca por `001284`/`ENT:001284` |
| QR/public token | Parcial | `public_token` existe e e unico; QR de `ENT:XXXXXX` precisa teste funcional dedicado |
| Oficina/entrega | Funcionando parcial | Entrega marca entrada e OS como entregue; regra permissiva |
| OS abrir/detalhe/status | Funcionando parcial | Status persiste; transicoes nao sao validadas por mapa |
| OS diagnostico | Funcionando parcial | Campo persiste via PATCH de status |
| OS adicionar peca | Nao conectado | Aba visual, sem backend |
| OS finalizar com estoque | Nao conectado | Nao existe consumo/baixa/estorno |
| Orcamento criar/aprovar/recusar | Nao conectado | Models existem, sem router/service |
| Orcamento nao baixar estoque | Nao testavel dinamicamente | Nao ha fluxo real de orcamento |
| Produtos listar/pesquisar/ver estoque | Funcionando como leitura | Usa `erp-products` |
| Produtos editar | Nao conectado | Sem endpoint/tela de edicao |
| Estoque saldo vs movimento | Concluido | 0 divergencias em `erp`; `public` vazio |
| Movimentacoes de estoque | Nao conectado | Model/tabela existem, sem endpoint |
| Venda balcao adicionar item | Mock/local | Carrinho em estado React |
| Venda balcao finalizar | Nao conectado | Botao desabilitado; sem backend |
| Venda baixa estoque | Nao testavel | Fluxo de finalizacao nao existe |
| Venda nao baixa duas vezes | Nao testavel | Nao ha endpoint/idempotencia |
| Venda rollback pagamento/estoque | Nao testavel | Nao ha endpoint |
| Cancelamento/estorno venda | Nao conectado | Sem endpoint |
| Pagamentos | Nao conectado | Model/tabela existem, sem router/service |
| Fornecedores | Nao conectado | Model/importador existem, sem UI/API |
| Localizacoes | Nao conectado | Model/importador existem, sem UI/API |
| Nota fiscal solicitada | Nao encontrado | Sem campo/workflow operacional de venda fiscal |
| Auditoria/logs | Parcial | Clientes, maquinas, entrada, OS status e print job registram; venda/estoque/orcamento nao existem |
| Concorrencia estoque | Nao implementado | Sem `SELECT FOR UPDATE`/transacao de baixa |
| Idempotencia operacoes criticas | Parcial | Importador usa chaves legadas; endpoints operacionais nao usam idempotency key |

## Testes dinamicos executados

| Comando | Resultado |
| --- | --- |
| `python -m pytest` | 6 passed, 1 warning |
| `python -m alembic current` | `0004_sicnet_migration_support (head)` |
| `python -m alembic heads` | `0004_sicnet_migration_support (head)` |
| `npm run build` | Passou, incluindo `tsc -b` |
| `python -m app.importers.sicnet.runner dry-run` | OK |
| `python -m ruff check .` | Nao executado: `No module named ruff` |

## Itens impossiveis de testar sem implementar antes

Estes itens nao foram ignorados; eles nao existem no codigo atual para serem executados de ponta a ponta:

- finalizar venda;
- registrar pagamento de venda;
- baixar estoque na venda;
- cancelar venda e estornar estoque;
- adicionar peca em OS;
- consumir peca em OS;
- estornar consumo de OS;
- criar orcamento com itens;
- aprovar/recusar orcamento;
- pagamento de OS;
- nota fiscal solicitada;
- E2E venda/estoque;
- E2E OS/consumo/estorno.

## Conclusao

O prompt foi fechado no limite maximo possivel sem criar novas regras de negocio. A auditoria confirmou que o nucleo de cadastro/entrada/OS basica funciona, mas os fluxos que envolvem dinheiro e estoque ainda precisam ser implementados antes de qualquer operacao real.

