# Mapa tecnico da auditoria do sistema

Data da auditoria: 2026-08-14

Projeto auditado: `C:\Users\geleia\OneDrive\Área de Trabalho\papai`

## Stack encontrada

| Camada | Tecnologia |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, Tailwind, React Router, TanStack Query, Axios, React Hook Form, Zod |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic, JWT |
| Banco | PostgreSQL no Supabase, schema `public` e schema `erp` |
| Importacao | Importador legado XLSX e importador SICNET SQL Server via `pyodbc` |
| Testes | Pytest no backend, build TypeScript/Vite no frontend |

## Rotas frontend

| Rota | Pagina | Backend chamado | Dados/acao | Status |
| --- | --- | --- | --- | --- |
| `/login` | `LoginPage` | `POST /auth/login` | Login JWT | Funcionando |
| `/` | `DashboardPage` | `/dashboard/metrics`, `/dashboard/database`, `/dashboard/workshop-flow` | Indicadores e fluxo da oficina | Funcionando |
| `/clientes` | `CustomersPage` | `GET /customers` | Lista e busca clientes | Funcionando |
| `/clientes/novo` | `NewCustomerPage` | `POST /customers` | Cria cliente | Funcionando |
| `/clientes/:id` | `CustomerDetailPage` | `GET /customers/{id}`, `GET /machines?customer_id=` | Detalhe e maquinas do cliente | Funcionando parcial, sem editar/inativar pela tela |
| `/maquinas` | `MachinesPage` | `GET /machines`, `GET /customers` | Lista maquinas com cliente | Funcionando |
| `/maquinas/nova` | `NewMachinePage` | `POST /machines`, `GET /customers` | Cria maquina vinculada ao cliente | Funcionando |
| `/entrada` | `MachineEntryPage` | `GET/POST /customers`, `GET/POST /machines`, `POST /machine-entries`, `POST /machine-entries/{id}/print-jobs` | Entrada, OS automatica e impressao | Funcionando parcial, sem idempotencia backend |
| `/oficina` | `MachinesInShopPage` | `GET /machine-entries/in-shop`, `POST /machine-entries/{id}/deliver` | Lista maquinas na oficina e entrega | Funcionando parcial |
| `/ordens-servico` | `WorkOrdersPage` | `GET /work-orders`, `GET /customers`, `GET /machines` | Lista OS | Funcionando |
| `/ordens-servico/:id` | `WorkOrderDetailPage` | `GET /work-orders/{id}/detail`, `PATCH /work-orders/{id}/status` | Detalhe, diagnostico e mudanca de status | Parcial, abas sem persistencia real |
| `/orcamentos` | `BudgetsPage` | `GET /work-orders?status=AGUARDANDO_APROVACAO` | Fila de OS aguardando aprovacao | Parcial, nao cria orcamento |
| `/produtos` | `ProductsPage` | `GET /erp-products`, `GET /erp-products/summary` | Consulta produtos importados | Funcionando como consulta |
| `/estoque` | `StockPage` | `GET /erp-products/summary` | Indicadores de estoque | Parcial, sem movimentacao |
| `/venda-balcao` | `CounterSalePage` | `GET /erp-products` | Carrinho local; botao finalizar desabilitado | Mock/parcial |

## Rotas backend

| Endpoint | Router | Service | Tabelas | Regra principal | Status |
| --- | --- | --- | --- | --- | --- |
| `POST /auth/login` | `auth.py` | `auth.authenticate_user` | `users`, `roles` | Valida senha e usuario ativo | Funcionando |
| `GET /auth/me` | `auth.py` | deps JWT | `users`, `roles` | Retorna usuario autenticado | Funcionando |
| `GET /dashboard/metrics` | `dashboard.py` | `dashboard.get_dashboard_metrics` | `machine_entries`, `work_orders` | Conta status operacionais | Funcionando |
| `GET /dashboard/database` | `dashboard.py` | `database.get_database_status` | conexao DB | Mostra modo de banco | Funcionando |
| `GET /dashboard/workshop-flow` | `dashboard.py` | `dashboard.get_workshop_flow` | `machine_entries`, `work_orders`, `customers`, `machines` | Fluxo resumido da oficina | Funcionando |
| `GET /customers` | `customers.py` | `customers.list_customers` | `customers` | Busca textual | Funcionando |
| `POST /customers` | `customers.py` | `customers.create_customer` | `customers`, `audit_logs` | Cria cliente e log | Funcionando parcial, sem normalizar/impedir documento duplicado |
| `GET /customers/{id}` | `customers.py` | `customers.get_customer_or_404` | `customers` | Consulta por ID | Funcionando |
| `PATCH /customers/{id}` | `customers.py` | `customers.update_customer` | `customers`, `audit_logs` | Atualiza cliente e log | Funcionando |
| `GET /machines` | `machines.py` | `machines.list_machines` | `machines` | Busca textual e filtro por cliente | Funcionando |
| `POST /machines` | `machines.py` | `machines.create_machine` | `machines`, `customers`, `audit_logs` | Exige cliente existente | Funcionando |
| `PATCH /machines/{id}` | `machines.py` | `machines.update_machine` | `machines`, `audit_logs` | Atualiza maquina | Funcionando |
| `POST /machine-entries` | `machine_entries.py` | `create_machine_entry_with_work_order` | `machine_entries`, `work_orders`, histories, audit | Cria entrada e uma OS na mesma transacao | Funcionando parcial, sem idempotency key |
| `GET /machine-entries/in-shop` | `machine_entries.py` | `list_machines_in_shop` | `machine_entries`, `work_orders`, `customers`, `machines`, `users` | Lista nao entregues | Funcionando |
| `POST /machine-entries/{id}/deliver` | `machine_entries.py` | `mark_machine_entry_delivered` | `machine_entries`, `work_orders`, history, audit | Marca entrega e status `ENTREGUE` | Funcionando parcial, permissivo |
| `POST /machine-entries/{id}/print-jobs` | `machine_entries.py` | `print_jobs.create_print_job` | `print_jobs`, audit | Registra impressao | Funcionando |
| `GET /work-orders` | `work_orders.py` | `list_work_orders` | `work_orders` | Lista/filtro status | Funcionando |
| `GET /work-orders/{id}/detail` | `work_orders.py` | `get_work_order_detail_or_404` | `work_orders`, `machine_entries`, `customers`, `machines`, history | Detalhe operacional | Funcionando |
| `PATCH /work-orders/{id}/status` | `work_orders.py` | `update_work_order_status` | `work_orders`, history, audit | Aceita qualquer status enum | Parcial, sem mapa de transicoes |
| `GET /erp-products` | `erp_products.py` | `list_erp_products` | `erp.produtos`, `erp.estoque_saldos`, `erp.precos_produto`, `erp.marcas` | Lista produtos importados | Funcionando como leitura |
| `GET /erp-products/summary` | `erp_products.py` | `get_erp_product_summary` | `erp.*` | Agregados de estoque/preco | Funcionando como leitura |
| `GET /imports/legacy-sic/analyze` | `imports.py` | `legacy_sic.analyze_legacy_workbook` | arquivo XLSX | Analise de planilha | Parcial, separado do importador SQL Server |

## Models sem endpoint operacional

| Model | Tabela | Situacao |
| --- | --- | --- |
| `Sale`, `SaleItem` | `sales`, `sale_items` | Modelo e tabela existem, sem router/service/frontend real |
| `Payment` | `payments` | Modelo e tabela existem, sem router/service |
| `Budget`, `BudgetItem`, `BudgetStatusHistory` | `budgets`, `budget_items`, `budget_status_history` | Modelo e tabela existem, sem router/service de criacao/aprovacao |
| `Part`, `Supplier`, `ProductLocation`, `StockMovement` | `parts`, `suppliers`, `product_locations`, `stock_movements` | Modelos existem e importador prepara dados, mas UI atual usa `erp.*` |

## Banco e migrations

| Migration | Papel | Status |
| --- | --- | --- |
| `0001_initial_schema` | Auth, clientes, maquinas, pecas, vendas, orcamentos, pagamentos, OS | Aplicada |
| `0002_operational_entry_printing` | Entrada operacional, impressao, status | Aplicada |
| `0003_product_allocation_support` | Schema `erp` e alocacoes | Aplicada |
| `0004_sicnet_migration_support` | Campos/constraints para importacao SICNET SQL Server | Aplicada |

Alembic atual: `0004_sicnet_migration_support (head)`.

## Supabase

| Area | Achado |
| --- | --- |
| Conexao | `DATABASE_URL` conecta com sucesso |
| Schema `erp` | Tem 10.777 produtos importados e RLS habilitado |
| Schema `public` | Tabelas operacionais existem; RLS desabilitado nas tabelas de negocio |
| Policies | Nenhuma policy listada para `public` e `erp` durante a auditoria |
| Multiempresa | Nao foi encontrado `company_id` nas tabelas operacionais |

