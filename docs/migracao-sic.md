# Migracao SIC - GELEIA.xlsx

## Fonte analisada

- Arquivo de trabalho: `data/GELEIA.xlsx`
- Origem preservada: `C:\Users\geleia\OneDrive\Documentos\GELEIA.xlsx`
- Data da analise: 2026-08-12
- Regra desta etapa: leitura, normalizacao, validacao e preview. Nenhuma importacao destrutiva foi implementada.

## Estrutura encontrada

| Aba | Linhas totais | Colunas | Linha de cabecalho | Registros |
| --- | ---: | ---: | ---: | ---: |
| Plan1 | 10.778 | 4 | 1 | 10.777 |

Cabecalhos encontrados:

| Cabecalho SIC | Campo alvo em `parts` |
| --- | --- |
| Codigo | `legacy_code` |
| Produto | `description` |
| Quantidade | `current_stock` |
| Valor | `sale_price` |

## Perfil das colunas

| Coluna | Preenchidos | Vazios | Tipos detectados |
| --- | ---: | ---: | --- |
| Codigo | 10.777 | 0 | int, str, datetime, float |
| Produto | 10.776 | 1 | str |
| Quantidade | 10.777 | 0 | int, str |
| Valor | 10.773 | 4 | int, str |

## Inconsistencias iniciais

- Codigos duplicados: 120 codigos distintos aparecem mais de uma vez.
- Exemplos de codigos duplicados: `335`, `100`, `2765`, `741`, `278`, `900206`, `526`, `529`, `332`, `234`.
- Descricoes vazias: 1 registro, na linha 2.
- Valores vazios: 4 registros.
- Precos invalidos: 0 detectados na primeira leitura.
- Quantidades invalidas: 0 detectadas na primeira leitura.
- Quantidades negativas: 1.126 registros.
- Primeiras linhas com quantidade negativa: 4, 24, 29, 47, 52, 53, 65, 69, 71, 89.

## Observacoes de migracao

1. `Codigo` deve ser preservado em `parts.legacy_code`, sem sobrescrever ou perder o codigo do SIC.
2. Como existem codigos duplicados, `legacy_code` nao foi modelado como unico.
3. `internal_code` foi criado separado e unico para permitir codificacao propria do novo ERP.
4. Estoque negativo foi mantido como inconsistencia, nao como erro fatal. A decisao de zerar, ajustar ou importar negativo precisa ser confirmada com a empresa.
5. Precos em formato brasileiro, como `15,99`, sao normalizados para decimal.
6. Linhas com descricao vazia devem ser revisadas antes da importacao definitiva.
7. O importador atual gera relatorio e preview; a persistencia em PostgreSQL deve ser adicionada apenas depois de aprovadas as regras de tratamento.

## Fluxo tecnico preparado

```text
Excel SIC
-> LegacySICImporter
-> leitura com openpyxl
-> mapeamento dos cabecalhos
-> normalizacao de codigo, quantidade e preco
-> validacao por linha
-> relatorio de inconsistencias
-> preview
-> importacao confirmada futuramente
```

Endpoint preparado:

```text
GET /api/v1/imports/legacy-sic/analyze
```
