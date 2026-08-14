import { PackageSearch } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { ErpProduct, ErpProductSummary } from "../types/domain";
import { getErrorMessage } from "../utils/errors";

async function fetchProducts(search: string) {
  const { data } = await api.get<ErpProduct[]>("/erp-products", {
    params: { search: search || undefined, limit: 200 },
  });
  return data;
}

async function fetchSummary() {
  const { data } = await api.get<ErpProductSummary>("/erp-products/summary");
  return data;
}

function money(value?: string | null) {
  return Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function quantity(value: string) {
  return Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 4 });
}

export function ProductsPage() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data: products = [], error: productsError, isLoading } = useQuery({
    queryKey: ["erp-products", debouncedSearch],
    queryFn: () => fetchProducts(debouncedSearch),
  });
  const { data: summary, error: summaryError } = useQuery({
    queryKey: ["erp-products-summary"],
    queryFn: fetchSummary,
  });
  const error = productsError || summaryError;

  return (
    <div className="space-y-5">
      <PageHeader
        title="Produtos"
        actions={
          <Link className="btn-secondary" to="/estoque">
            Abrir estoque
          </Link>
        }
      />

      {error ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {getErrorMessage(error)}
        </div>
      ) : null}

      <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Dados importados do SIC. A planilha atual trouxe código, produto, quantidade e valor; alocações físicas não vieram na importação e aparecem como não informadas.
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard title="Produtos" value={summary?.total_produtos ?? 0} icon={PackageSearch} />
        <MetricCard title="Ativos" value={summary?.produtos_ativos ?? 0} icon={PackageSearch} />
        <div className="rounded-md border border-stone-200 bg-white p-4 shadow-sm">
          <span className="text-sm font-medium text-stone-600">Valor estimado de venda</span>
          <strong className="mt-3 block text-2xl font-semibold tracking-normal text-stone-950">
            {money(summary?.valor_total_estoque_venda)}
          </strong>
          <p className="mt-1 text-xs text-amber-700">Base pendente de conferência</p>
        </div>
      </section>

      <section className="surface p-3">
        <SearchField
          value={search}
          onChange={setSearch}
          placeholder="Buscar por codigo, SKU, descricao ou marca"
          ariaLabel="Buscar produtos"
        />
      </section>

      <div className="overflow-hidden rounded-md border border-stone-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="bg-stone-50 text-left text-xs font-semibold uppercase tracking-normal text-stone-600">
              <tr>
                <th className="px-4 py-3">SKU</th>
                <th className="px-4 py-3">Descricao</th>
                <th className="px-4 py-3">Marca</th>
                <th className="px-4 py-3">Un</th>
                <th className="px-4 py-3">Alocação</th>
                <th className="px-4 py-3 text-right">Estoque</th>
                <th className="px-4 py-3 text-right">Preco</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {products.map((product) => (
                <tr key={product.produto_id} className="hover:bg-stone-50">
                  <td className="px-4 py-3 font-medium text-stone-950">{product.sku || "-"}</td>
                  <td className="px-4 py-3 text-stone-800">{product.descricao}</td>
                  <td className="px-4 py-3 text-stone-700">{product.marca || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">{product.unidade}</td>
                  <td className="px-4 py-3 text-stone-700">
                    {product.alocacao ? product.alocacao : <span className="text-stone-400">Não informada</span>}
                    {product.local_estoque ? <span className="block text-xs text-stone-500">{product.local_estoque}</span> : null}
                  </td>
                  <td className={`px-4 py-3 text-right ${Number(product.estoque) < 0 ? "font-semibold text-red-700" : "text-stone-700"}`}>
                    {quantity(product.estoque)}
                  </td>
                  <td className="px-4 py-3 text-right text-stone-700">{money(product.preco_venda)}</td>
                </tr>
              ))}
              {!isLoading && products.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-stone-500" colSpan={7}>
                    Nenhum produto encontrado no schema erp do Supabase.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
