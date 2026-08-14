# SICNET customers import report

Generated at: 2026-08-14

Importacao parcial executada para resolver a aba Clientes.

## Escopo

- Origem: SQL Server `SICNET_MIGRACAO`, tabela `dbo.TABCLI`
- Destino: Supabase/PostgreSQL, tabela `public.customers`
- Tipo: upsert idempotente por `legacy_source + legacy_sic_id`
- Itens nao alterados: produtos, estoque, fornecedores, localizacoes, maquinas, OS, vendas e pagamentos

## Resultado

| Metrica | Valor |
| --- | ---: |
| Clientes lidos do SICNET | 7.677 |
| Clientes antes da carga | 0 |
| Clientes depois da carga | 7.677 |
| Clientes com `legacy_source = SICNET` | 7.677 |
| Clientes com documento preenchido | 2.151 |
| Grupos de documentos duplicados | 44 |

## Validacao

A API de producao `GET /_/backend/api/v1/customers?limit=5` retornou `200` com clientes importados.

Observacao: documentos duplicados foram preservados como vieram do SICNET. Nao foi feito merge automatico nesta etapa.

