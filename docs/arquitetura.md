# Arquitetura Inicial

## Decisoes principais

- O ERP foi separado em `backend`, `frontend`, `docs` e `data` para manter API, interface, documentacao e arquivos legados isolados.
- A API usa FastAPI com camadas de `api`, `schemas`, `repositories` e `services`. Controllers ficam finos; regra de negocio entra em services.
- A persistencia usa SQLAlchemy 2 e Alembic. A migration inicial cria a base relacional para oficina, orcamentos, estoque, vendas, pagamentos e auditoria.
- O estoque e unico para balcao e oficina. Saidas futuras por venda ou uso em OS devem escrever em `stock_movements` e atualizar `parts.current_stock` dentro da mesma transacao.
- `parts.legacy_code` preserva o codigo do SIC e nao e unico porque a planilha atual possui duplicidades.
- Entrada de maquina e entidade propria (`machine_entries`) e origina uma OS, sem misturar recebimento com execucao do servico.
- OS e orcamentos possuem tabelas de historico de status para evitar sobrescrita de eventos.
- A autenticacao inicial usa JWT com access token e refresh token. Senhas sao armazenadas com hash.
- Auditoria foi modelada como tabela generica (`audit_logs`) com usuario, acao, entidade, dados antes/depois e IP quando disponivel.
- O importador SIC e somente leitura nesta fase. Ele analisa, normaliza, valida e gera preview sem gravar dados no banco.

## Fronteiras de crescimento

- Fluxos fiscais, anexos/fotos, aprovacao formal de orcamento e PDV completo ainda devem entrar em novas migrations e services.
- Antes de importar produtos, e necessario decidir tratamento de estoque negativo, codigos duplicados e registros sem descricao.
- Sequenciais legiveis foram implementados de forma simples para desenvolvimento. Em producao, a geracao deve evoluir para uma sequencia transacional no PostgreSQL.
