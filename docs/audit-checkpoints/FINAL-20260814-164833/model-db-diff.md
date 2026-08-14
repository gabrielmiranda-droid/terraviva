# Diff SQLAlchemy models vs Supabase schema

Data da auditoria: 2026-08-14

Comparacao feita em modo leitura entre `Base.metadata` e o banco apontado por `DATABASE_URL`.

## Resultado

- Tabelas em models: 20
- Tabelas ausentes no banco: 0
- Tabelas extras no banco, sem model SQLAlchemy direto: 8
- Tabelas com diferenca de colunas/nullability: 0

## Tabelas ausentes no banco

Nenhuma.

## Tabelas extras no banco

- `erp.filiais`
- `erp.locais_estoque`
- `erp.marcas`
- `erp.unidades_medida`
- `erp.produtos`
- `erp.precos_produto`
- `erp.estoque_movimentos`
- `erp.estoque_saldos`

## Diferencas por tabela

Nenhuma diferenca estrutural relevante de coluna/nullability detectada para as tabelas modeladas.
