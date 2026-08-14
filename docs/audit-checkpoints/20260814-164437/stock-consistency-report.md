# Relatorio de consistencia de estoque

Data da auditoria: 2026-08-14

Escopo executado em modo leitura contra o Supabase configurado no projeto `papai`.

## Resumo

O sistema tem duas estruturas de estoque coexistindo:

- `erp.estoque_saldos` / `erp.estoque_movimentos`, usadas hoje pelas telas de produtos, estoque e venda balcao.
- `public.parts.current_stock` / `public.stock_movements`, preparadas para o ERP operacional e para o importador SICNET SQL Server.

Resultado principal: o estoque importado no schema `erp` esta internamente consistente, mas o fluxo operacional real ainda nao usa esse estoque para venda, OS, pagamentos ou consumo de pecas. O schema `public` ainda esta vazio para produtos e movimentacoes.

## Fonte de verdade encontrada

| Area | Fonte lida pelo frontend | Tabela de saldo | Tabela de movimento | Status |
| --- | --- | --- | --- | --- |
| Produtos | `/api/v1/erp-products` | `erp.estoque_saldos.quantidade` | `erp.estoque_movimentos.quantidade` | Consistente para consulta |
| Estoque | `/api/v1/erp-products/summary` | `erp.estoque_saldos.quantidade` | `erp.estoque_movimentos.quantidade` | Consistente para consulta |
| Venda balcao | Busca produtos em `/erp-products`, mas nao finaliza venda | Nao baixa | Nao grava | Nao conectado |
| OS / consumo | Nao ha endpoint de consumo | Nao baixa | Nao grava | Nao conectado |
| ERP operacional novo | Sem tela/endpoint CRUD ativo para pecas | `public.parts.current_stock` | `public.stock_movements` | Estrutura criada, sem dados |

## Totais no Supabase

| Tabela | Registros |
| --- | ---: |
| `erp.produtos` | 10.777 |
| `erp.estoque_saldos` | 10.777 |
| `erp.estoque_movimentos` | 10.777 |
| `erp.precos_produto` | 10.777 |
| `public.parts` | 0 |
| `public.stock_movements` | 0 |
| `public.sales` | 0 |
| `public.sale_items` | 0 |
| `public.payments` | 0 |

## Consistencia `erp`

Comparacao feita:

```sql
erp.estoque_saldos.quantidade
versus
sum(erp.estoque_movimentos.quantidade)
por produto_id e local_estoque_id
```

Resultado:

| Checagem | Resultado |
| --- | ---: |
| Grupos divergentes | 0 |
| Soma dos saldos | 227.131,6100 |
| Soma dos movimentos | 227.131,6100 |
| Produtos com estoque negativo | 1.126 |
| Produtos com estoque zerado | 5.111 |
| Produtos com estoque positivo | 4.540 |
| Produtos sem preco ou preco zero | 16 |
| Produtos sem linha de saldo | 0 |
| Grupos de SKU duplicado | 120 |
| Grupos de descricao duplicada | 258 |

Conclusao: a carga inicial em `erp` esta coerente entre saldo e movimento inicial. Os negativos, zerados e duplicados parecem vir da base importada e devem ser revisados antes de usar em venda real.

## Consistencia `public`

Comparacao feita:

```sql
public.parts.current_stock
versus
sum(public.stock_movements.quantity)
por part_id
```

Resultado:

| Checagem | Resultado |
| --- | ---: |
| Pecas | 0 |
| Movimentos | 0 |
| Grupos divergentes | 0 |
| Pecas negativas | 0 |
| Pecas sem preco | 0 |
| Pecas sem fornecedor | 0 |
| Pecas sem localizacao | 0 |

Conclusao: nao ha divergencia porque ainda nao ha dados operacionais em `public.parts`.

## Riscos criticos

1. Existem duas bases de produto/estoque (`erp.*` e `public.parts`) com finalidades diferentes. Antes de ativar venda/OS, e necessario escolher uma fonte operacional unica ou criar uma camada clara de sincronizacao.
2. Venda balcao mostra estoque de `erp.estoque_saldos`, mas nao existe endpoint para criar venda, pagamento ou baixa de estoque.
3. OS tem abas de pecas/financeiro/orcamento, mas nao possui backend para consumo real, estorno ou movimentacao.
4. Nao foi encontrado lock pessimista, `SELECT FOR UPDATE`, constraint de estoque minimo, idempotency key, nem atualizacao atomica para baixa de estoque.
5. Como nao existe finalizacao de venda, nao foi possivel validar rollback de venda/pagamento/estoque ponta a ponta.

## SQL de auditoria usado

```sql
select count(*) from (
  select es.produto_id, es.local_estoque_id, es.quantidade, coalesce(sum(em.quantidade),0) mov_sum
  from erp.estoque_saldos es
  left join erp.estoque_movimentos em
    on em.produto_id = es.produto_id
   and em.local_estoque_id = es.local_estoque_id
  group by es.produto_id, es.local_estoque_id, es.quantidade
  having es.quantidade <> coalesce(sum(em.quantidade),0)
) x;
```

```sql
select count(*) from (
  select p.id
  from public.parts p
  left join public.stock_movements sm on sm.part_id = p.id
  group by p.id, p.current_stock
  having p.current_stock <> coalesce(sum(sm.quantity),0)
) x;
```

