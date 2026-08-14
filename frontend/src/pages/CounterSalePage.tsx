import { Minus, Plus, Search, ShoppingCart } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { ErpProduct } from "../types/domain";

type CartItem = ErpProduct & { quantity: number };

async function fetchProducts(search: string) {
  if (!search.trim()) return [];
  const { data } = await api.get<ErpProduct[]>("/erp-products", { params: { search, limit: 30 } });
  return data;
}

function money(value?: string | number | null) {
  return Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function CounterSalePage() {
  const [search, setSearch] = useState("");
  const [submittedSearch, setSubmittedSearch] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const { data: products = [] } = useQuery({
    queryKey: ["counter-sale-products", submittedSearch],
    queryFn: () => fetchProducts(submittedSearch),
  });
  const total = useMemo(
    () => cart.reduce((sum, item) => sum + Number(item.preco_venda ?? 0) * item.quantity, 0),
    [cart],
  );

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    setSubmittedSearch(search);
  }

  function addProduct(product: ErpProduct) {
    setCart((current) => {
      const existing = current.find((item) => item.produto_id === product.produto_id);
      if (existing) {
        return current.map((item) =>
          item.produto_id === product.produto_id ? { ...item, quantity: item.quantity + 1 } : item,
        );
      }
      return [...current, { ...product, quantity: 1 }];
    });
  }

  function decrement(productId: number) {
    setCart((current) =>
      current
        .map((item) => (item.produto_id === productId ? { ...item, quantity: item.quantity - 1 } : item))
        .filter((item) => item.quantity > 0),
    );
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Venda Balcão" />

      <section className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          <form className="surface flex gap-2 p-4" onSubmit={handleSearch}>
            <label className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={17} />
              <input
                className="form-field pl-9"
                placeholder="Buscar por código, SKU, descrição ou marca"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
            <button className="btn-secondary" type="submit">
              Buscar
            </button>
          </form>

          <div className="grid gap-3 md:grid-cols-2">
            {products.map((product) => (
              <button
                key={product.produto_id}
                className="rounded-md border border-stone-200 bg-white p-4 text-left shadow-sm transition hover:border-field-700 hover:bg-field-50"
                type="button"
                onClick={() => addProduct(product)}
              >
                <p className="font-semibold text-stone-950">{product.descricao}</p>
                <p className="text-xs text-stone-500">{[product.sku, product.marca].filter(Boolean).join(" · ") || "-"}</p>
                <div className="mt-3 flex items-center justify-between text-sm">
                  <span className="text-stone-600">Estoque {Number(product.estoque).toLocaleString("pt-BR")}</span>
                  <strong>{money(product.preco_venda)}</strong>
                </div>
              </button>
            ))}
          </div>

          {submittedSearch && products.length === 0 ? (
            <EmptyState
              icon={Search}
              title="Nenhum produto encontrado"
              description="Busque por código, SKU, descrição ou marca para adicionar ao carrinho."
            />
          ) : null}
        </div>

        <aside className="surface h-fit p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-stone-950">Carrinho</h2>
              <p className="text-sm text-stone-600">Consumidor final</p>
            </div>
            <ShoppingCart className="text-field-800" size={22} aria-hidden="true" />
          </div>

          <div className="mt-4 space-y-3">
            {cart.map((item) => (
              <div key={item.produto_id} className="rounded-md border border-stone-200 p-3">
                <p className="text-sm font-semibold text-stone-950">{item.descricao}</p>
                <div className="mt-2 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <button className="icon-button" type="button" onClick={() => decrement(item.produto_id)}>
                      <Minus size={15} aria-hidden="true" />
                    </button>
                    <span className="w-8 text-center text-sm font-semibold">{item.quantity}</span>
                    <button className="icon-button" type="button" onClick={() => addProduct(item)}>
                      <Plus size={15} aria-hidden="true" />
                    </button>
                  </div>
                  <strong className="text-sm">{money(Number(item.preco_venda ?? 0) * item.quantity)}</strong>
                </div>
              </div>
            ))}
            {cart.length === 0 ? (
              <EmptyState
                icon={ShoppingCart}
                title="Carrinho vazio"
                description="Busque produtos e adicione itens para iniciar a venda."
              />
            ) : null}
          </div>

          <div className="mt-4 border-t border-stone-200 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-stone-600">Total</span>
              <strong className="text-2xl text-stone-950">{money(total)}</strong>
            </div>
            <button className="btn-primary mt-4 w-full" type="button" disabled>
              Finalizar venda
            </button>
            <p className="mt-2 text-xs text-stone-500">
              Finalização e baixa de estoque serão conectadas ao módulo fiscal/financeiro na próxima etapa.
            </p>
          </div>
        </aside>
      </section>
    </div>
  );
}
