# Backup antes da importacao SICNET

Antes de executar a importacao real do banco `SICNET_MIGRACAO`, gere um backup recuperavel do Supabase.

```powershell
pg_dump "$env:DATABASE_URL" --format=custom --file ".\backups\pre-sicnet-import.dump"
```

Valide que o arquivo foi criado e mantenha-o fora do git.

Regras:

- nao executar `import-all` sem revisar o dry-run;
- nao gravar nada no banco SQL Server `SICNET_MIGRACAO`;
- nao importar historico antigo de vendas, caixa, contas, orcamentos, notas, logs ou movimentacoes antigas nesta fase;
- preservar estoque negativo para auditoria.

