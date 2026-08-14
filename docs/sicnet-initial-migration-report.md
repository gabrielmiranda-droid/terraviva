# SICNET initial migration dry-run

Generated at: 2026-08-14T16:25:43
Source database: `SICNET_MIGRACAO`

No import was executed in this dry-run.

## Source SQL Server

- `TABCLI`: 7677 rows, 45 columns
  - duplicate documents: 46
- `TABFOR`: 341 rows, 17 columns
  - duplicate documents: 1
- `TABEST1`: 10790 rows, 54 columns
  - negative stock: 1126
  - zero stock: 5125
  - below minimum stock: 5626
  - missing supplier link: 18
  - missing location link: 14
  - missing/zero cost: 17
  - missing/zero sale price: 16
  - positive quantity total: 241019.47
  - duplicate legacy codes: 0
  - duplicate internal codes: 3
  - duplicate barcodes: 0
- `TABEST8`: 2488 rows, 3 columns

- `TABEST1.lksetor -> TABEST8.controle` orphan links: 10

## Destination Supabase/PostgreSQL

- Dialect: `postgresql`
- Alembic revision: `0004_sicnet_migration_support`

### Counts

- `public.customers`: 0
- `public.suppliers`: 0
- `public.parts`: 0
- `public.product_locations`: 0
- `public.stock_movements`: 0
- `erp.produtos`: 10777
- `erp.estoque_saldos`: 10777

## Commands

Dry-run:

```powershell
python -m app.importers.sicnet.runner dry-run
```

Real import, only after review and backup:

```powershell
python -m app.importers.sicnet.runner import-all --confirm-import
```
