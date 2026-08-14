# Migracao SICNET para Supabase

O importador fica em `backend/app/importers/sicnet`.

Ele migra apenas a base inicial operacional:

- clientes de `dbo.TABCLI` para `customers`;
- fornecedores de `dbo.TABFOR` para `suppliers`;
- localizacoes/setores de `dbo.TABEST8` para `product_locations`;
- produtos/pecas de `dbo.TABEST1` para `parts`;
- saldo atual de `TABEST1.quantidade` para `parts.current_stock`;
- movimento auditavel `SALDO_INICIAL_MIGRACAO` em `stock_movements`.

Nao importa historico antigo nesta fase.

## Variaveis

No `.env` da raiz do projeto:

```env
DATABASE_URL=postgresql+psycopg://...
SICNET_DB_HOST=localhost
SICNET_DB_NAME=SICNET_MIGRACAO
SICNET_DB_DRIVER=ODBC Driver 18 for SQL Server
SICNET_DB_TRUSTED_CONNECTION=true
```

Se precisar usuario/senha no SQL Server:

```env
SICNET_DB_TRUSTED_CONNECTION=false
SICNET_DB_USER=...
SICNET_DB_PASSWORD=...
```

## Comandos

Instalar dependencias:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Aplicar schema:

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Dry-run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.importers.sicnet.runner dry-run
```

Importacao real, somente depois de revisar backup e dry-run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.importers.sicnet.runner import-all --confirm-import
```

