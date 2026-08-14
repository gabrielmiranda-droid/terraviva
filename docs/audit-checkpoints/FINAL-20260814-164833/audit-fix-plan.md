# Plano de correcao pos-auditoria

Data: 2026-08-14

Este plano prioriza seguranca operacional. A recomendacao e nao colocar venda/OS com estoque em producao antes da Fase 1.

## Fase 1 - Problemas criticos

1. Definir a fonte oficial de produto/estoque:
   - Opção A: migrar `erp.produtos` para `public.parts` e passar o app a usar `public.parts`.
   - Opção B: manter `erp.*` como fonte operacional e criar models/services de venda/OS sobre `erp`.
   - Recomendacao tecnica: usar `public.parts` como modelo operacional e tratar `erp.*` como staging/legado.

2. Criar service atomico de estoque:
   - baixa;
   - entrada;
   - ajuste;
   - estorno;
   - validacao de estoque negativo;
   - registro obrigatorio em `stock_movements`.

3. Implementar concorrencia:
   - `SELECT ... FOR UPDATE` no produto/saldo durante baixa;
   - transacao unica;
   - erro claro para estoque insuficiente;
   - teste simulando disputa pela ultima unidade.

4. Implementar idempotencia:
   - tabela ou campo de `idempotency_key`;
   - obrigatorio para finalizar venda, consumir peca, estornar e criar entrada;
   - repetir a mesma requisicao deve retornar o mesmo resultado, nao duplicar movimento.

5. Implementar venda balcao real:
   - endpoint de finalizacao;
   - criar `sale`;
   - criar `sale_items`;
   - recalcular total no backend;
   - criar `payment`;
   - baixar estoque;
   - rollback se qualquer etapa falhar.

6. Implementar cancelamento de venda:
   - venda finalizada nao deve ser editada silenciosamente;
   - cancelamento cria movimento inverso;
   - pagamentos devem ser cancelados/estornados conforme status.

## Fase 2 - Fluxos operacionais

1. OS com pecas:
   - adicionar item planejado nao baixa estoque;
   - consumir peca baixa estoque;
   - remover consumo gera estorno;
   - historico sempre auditavel.

2. Orcamento:
   - criar orcamento;
   - adicionar pecas e servicos;
   - versionar;
   - aprovar;
   - recusar;
   - nao baixar estoque so por existir.

3. Regras de status da OS:
   - criar mapa de transicoes validas;
   - bloquear retorno indevido como `ENTREGUE -> EM_DIAGNOSTICO`;
   - registrar motivo em transicoes criticas.

4. Entrada de maquina:
   - adicionar idempotency key;
   - garantir que uma entrada gere uma unica OS;
   - aceitar busca por `001284` e `ENT:001284`.

5. Fornecedores e localizacoes:
   - CRUD basico;
   - vinculo com produto;
   - filtros de produtos sem fornecedor/localizacao.

## Fase 3 - Seguranca

1. Rotacionar senha do banco exposta em captura/arquivo.
2. Revisar `.env` e garantir que nao seja commitado.
3. Definir estrategia de RLS:
   - se backend for unico acesso ao banco, documentar isso;
   - se frontend usar Supabase direto, criar policies antes.
4. Implementar permissoes por papel:
   - estoque;
   - vendedor;
   - financeiro;
   - mecanico;
   - admin.
5. Avaliar `company_id` se houver chance real de multiempresa.

## Fase 4 - Performance e operacao

1. Criar indices para buscas reais:
   - produto por SKU, descricao, codigo legado, barcode;
   - cliente por documento normalizado;
   - OS por numero e status.
2. Paginar endpoints de listagem com total/count.
3. Criar relatorios de divergencia de estoque recorrentes.
4. Criar rotina de backup antes de importacao real SICNET.
5. Criar logs estruturados para operacoes criticas.

## Fase 5 - UX

1. Venda balcao:
   - selecionar cliente opcional;
   - consumidor final;
   - pagamento;
   - nota fiscal solicitada;
   - feedback de estoque insuficiente.
2. OS:
   - telas reais para pecas, servicos, financeiro e fotos;
   - botoes por proxima acao valida.
3. Estoque:
   - tela de ajuste;
   - historico por produto;
   - alerta de negativo, zerado e sem preco.
4. Produtos:
   - edicao controlada;
   - revisao de duplicados;
   - filtro de pendencias SICNET.

## Testes a criar primeiro

| Fluxo | Teste |
| --- | --- |
| Venda | finalizar venda baixa estoque uma vez |
| Venda | finalizar duas vezes com mesma idempotency key nao duplica |
| Venda | estoque insuficiente faz rollback |
| Venda | cancelamento gera estorno |
| OS | adicionar peca ao orcamento nao baixa estoque |
| OS | consumir peca baixa estoque |
| OS | estornar consumo devolve estoque |
| Entrada | clique duplo nao cria duas OS |
| Importador | rodar importacao duas vezes nao duplica legado |
| Estoque | `current_stock` sempre bate com soma dos movimentos |

## Ordem recomendada de implementacao

1. Escolher fonte oficial de estoque.
2. Criar testes de estoque esperados, mesmo falhando inicialmente.
3. Criar service atomico de estoque.
4. Criar venda balcao backend.
5. Conectar tela de venda balcao.
6. Criar consumo de pecas em OS.
7. Criar orcamento real.
8. Rodar importacao SICNET real somente depois da decisao de fonte oficial e backup.

## Criterio de pronto para operacao real

O ERP so deve ser considerado pronto para operar venda/estoque quando estes pontos estiverem verdes:

- uma unica fonte oficial de saldo definida;
- toda baixa gera `stock_movements`;
- saldo armazenado bate com soma dos movimentos;
- venda finalizada cria venda, itens, pagamento e movimento em uma transacao;
- falha em qualquer etapa faz rollback;
- cancelamento cria movimento inverso;
- consumo em OS baixa apenas quando a peca for realmente consumida;
- orcamento nao baixa estoque por existir ou por ser aprovado, salvo regra explicita;
- endpoints criticos usam idempotency key;
- teste automatizado cobre venda, cancelamento, OS, estorno e concorrencia.
