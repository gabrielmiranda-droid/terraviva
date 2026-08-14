import { PackageSearch, Search, TriangleAlert, Warehouse } from "lucide-react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { ErpProductSummary } from "../types/domain";

async function fetchSummary() {
  const { data } = await api.get<ErpProductSummary>("/erp-products/summary");
  return data;
}

function money(value?: string | null) {
  return Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function StockPage() {
  const { data: summary } = useQuery({ queryKey: ["erp-products-summary"], queryFn: fetchSummary });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Estoque"
        actions={
          <Link className="btn-secondary" to="/produtos">
            Produtos
          </Link>
        }
      />

      <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Dado estimado. A base importada ainda precisa de conferência; a planilha atual não trouxe alocação física das peças.
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Produtos importados" value={summary?.total_produtos ?? 0} icon={PackageSearch} />
        <MetricCard title="Estoque negativo" value={summary?.produtos_com_estoque_negativo ?? 0} icon={TriangleAlert} />
        <MetricCard title="Produtos ativos" value={summary?.produtos_ativos ?? 0} icon={Warehouse} />
        <div className="surface p-4">
          <span className="text-sm font-medium text-stone-600">Valor estimado em venda</span>
          <strong className="mt-3 block text-2xl font-semibold text-stone-950">
            {money(summary?.valor_total_estoque_venda)}
          </strong>
        </div>
      </section>

      <section className="surface p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-stone-950">Auditoria de Importação</h2>
            <p className="text-sm text-stone-600">Fila inicial de conferência da base SIC.</p>
          </div>
          <Link className="btn-secondary" to="/produtos">
            <Search size={17} aria-hidden="true" />
            Conferir produtos
          </Link>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p className="text-sm font-semibold text-stone-950">Estoque negativo</p>
            <p className="mt-1 text-sm text-stone-600">Priorizar revisão de quantidade física e histórico.</p>
          </div>
          <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p className="text-sm font-semibold text-stone-950">Preços suspeitos</p>
            <p className="mt-1 text-sm text-stone-600">Validar itens com preço zerado, muito alto ou fora de padrão.</p>
          </div>
          <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p className="text-sm font-semibold text-stone-950">Alocações faltantes</p>
            <p className="mt-1 text-sm text-stone-600">Importar endereço físico quando houver exportação com prateleira, gaveta ou posição.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
