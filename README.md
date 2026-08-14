# ERP de Oficina Agricola

Fundacao inicial de um ERP para oficina mecanica de maquinas agricolas com venda de pecas no balcao. Esta etapa cria backend FastAPI, frontend React, PostgreSQL em Docker, autenticação base, modelagem inicial, migration, seed de administrador e analisador da planilha legado SIC.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic, JWT, Pytest
- Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios, React Hook Form, Zod
- Infra: Docker Compose, PostgreSQL

## Execucao local com Docker

```bash
cp .env.example .env
docker compose up --build
```

Acessos:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Usando banco existente no Supabase

Se voce ja carregou os SQLs no Supabase, use o projeto com `DATABASE_URL`.

1. Copie `.env.supabase.example` para `.env`.
2. Preencha `DATABASE_URL` com a connection string do Supabase em formato SQLAlchemy:

```text
postgresql+psycopg://postgres:SUA_SENHA@db.tylzdvyaraowcbptrctr.supabase.co:5432/postgres?sslmode=require
```

O `.env` ja foi preenchido com o projeto `tylzdvyaraowcbptrctr`; falta apenas trocar `COLOQUE-SUA-SENHA-AQUI` pela senha real do banco.

3. Suba sem Postgres local:

```bash
docker compose -f docker-compose.supabase.yml up --build
```

Se for rodar sem Docker:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Ou use o script:

```powershell
cd backend
.\scripts\dev_supabase.ps1
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Com o schema `erp` ja carregado no Supabase, a tela `Produtos e Estoque` usa:

- `GET /api/v1/erp-products`
- `GET /api/v1/erp-products/summary`

Supabase CLI:

```bash
npx supabase login
npx supabase init
npx supabase link --project-ref tylzdvyaraowcbptrctr
```

O projeto ja possui `supabase/config.toml`; por isso `npx supabase init` pode avisar que o arquivo ja existe. Nesse caso, siga para o `link`.

Se preferir nao abrir navegador automaticamente:

```bash
npx supabase login --no-browser
```

O `link` exige que o login tenha sido feito ou que `SUPABASE_ACCESS_TOKEN` esteja definido no seu ambiente.

Importante: a chave `SUPABASE_PUBLISHABLE_KEY` sozinha nao conecta o backend ao schema `erp`. Para ver os produtos reais no localhost, o `DATABASE_URL` precisa ter a senha real do Postgres do Supabase e o backend deve ser iniciado sem `scripts/dev_sqlite.py`.

Credencial inicial de desenvolvimento:

- Email: `admin@geleia.local`
- Senha: `123456`

## Comandos uteis

Backend local:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Fallback sem Docker/PostgreSQL, apenas para navegar e testar telas:

```bash
cd backend
python scripts/dev_sqlite.py
```

Frontend local:

```bash
cd frontend
npm install
npm run dev
```

Testes:

```bash
cd backend
pytest
```

Build frontend:

```bash
cd frontend
npm run build
```

## Troubleshooting

- Se `docker compose up --build` retornar erro 500 ao consultar `dockerDesktopLinuxEngine`, reinicie o Docker Desktop e execute `docker version` antes de tentar novamente. O `docker-compose.yml` foi validado com `docker compose config`.
- O `npm audit --omit=dev` ainda aponta vulnerabilidades moderadas em `react-router@6.30.4`. A correcao disponivel exige migrar para React Router mais novo com React 19; planeje essa atualizacao antes de producao.

## Arquitetura

O backend segue separacao por camadas:

- `app/api`: rotas HTTP e dependencias
- `app/models`: modelos SQLAlchemy
- `app/schemas`: schemas Pydantic
- `app/repositories`: consultas persistentes
- `app/services`: regras de negocio
- `app/importers`: leitura e validacao de arquivos legados
- `alembic`: migrations

O frontend separa:

- `src/pages`: telas principais
- `src/layouts`: layout autenticado
- `src/components`: componentes reutilizaveis
- `src/services`: cliente HTTP
- `src/hooks`: contexto de autenticacao
- `src/routes`: roteamento
- `src/types`: tipos de dominio

## Migração SIC

A planilha `data/GELEIA.xlsx` foi copiada de uma origem local preservada e analisada sem alteracao destrutiva. O relatorio esta em `docs/migracao-sic.md`.

O importador atual faz apenas analise e preview. A importacao definitiva para `parts` e `stock_movements` deve ser implementada apos validar as regras para codigos duplicados, descricoes vazias e estoque negativo.
