import { Minus, Plus, Search, ShoppingCart } from "lucide-react";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { Customer, ErpProduct } from "../types/domain";

type CartItem = ErpProduct & { quantity: number };

async function fetchProducts(search: string) {
  if (!search.trim()) return [];
  const { data } = await api.get<ErpProduct[]>("/erp-products", { params: { search, limit: 30 } });
  return data;
}

async function fetchCustomers(search: string) {
  if (!search.trim()) return [];
  const { data } = await api.get<Customer[]>("/customers", { params: { search, limit: 10 } });
  return data;
}

function money(value?: string | number | null) {
  return Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function CounterSalePage() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const [customerSearch, setCustomerSearch] = useState("");
  const debouncedCustomerSearch = useDebouncedValue(customerSearch);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [fiscalInvoiceRequested, setFiscalInvoiceRequested] = useState(false);
  const [fiscalData, setFiscalData] = useState({
    fiscal_document: "",
    fiscal_name: "",
    fiscal_state_registration: "",
    fiscal_email: "",
  });
  const { data: products = [] } = useQuery({
    queryKey: ["counter-sale-products", debouncedSearch],
    queryFn: () => fetchProducts(debouncedSearch),
  });
  const { data: customers = [] } = useQuery({
    queryKey: ["counter-sale-customers", debouncedCustomerSearch],
    queryFn: () => fetchCustomers(debouncedCustomerSearch),
  });
  const total = useMemo(
    () => cart.reduce((sum, item) => sum + Number(item.preco_venda ?? 0) * item.quantity, 0),
    [cart],
  );

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

  function selectCustomer(customer: Customer) {
    setSelectedCustomer(customer);
    setCustomerSearch(customer.name);
    setFiscalData({
      fiscal_document: customer.document ?? "",
      fiscal_name: customer.trade_name || customer.name,
      fiscal_state_registration: customer.state_registration ?? "",
      fiscal_email: customer.email ?? "",
    });
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Venda Balcão" />

      <section className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          <section className="surface p-4">
            <SearchField
              value={search}
              onChange={setSearch}
              placeholder="Buscar por codigo, SKU, descricao ou marca"
              ariaLabel="Buscar produtos da venda"
            />
          </section>

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

          {debouncedSearch && products.length === 0 ? (
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

          <div className="mt-4 border-t border-stone-200 pt-4">
            <label className="block space-y-1">
              <span className="label">Cliente</span>
              <input
                className="form-field"
                placeholder="Consumidor final ou buscar cliente"
                value={customerSearch}
                onChange={(event) => {
                  setCustomerSearch(event.target.value);
                  setSelectedCustomer(null);
                }}
              />
            </label>
            {customerSearch && !selectedCustomer && customers.length > 0 ? (
              <div className="mt-2 max-h-44 overflow-auto rounded-md border border-stone-200 bg-white">
                {customers.map((customer) => (
                  <button
                    key={customer.id}
                    className="block w-full px-3 py-2 text-left text-sm hover:bg-stone-50"
                    type="button"
                    onClick={() => selectCustomer(customer)}
                  >
                    <span className="font-semibold text-stone-950">{customer.name}</span>
                    <span className="block text-xs text-stone-500">{customer.document || customer.email || "Sem dados fiscais"}</span>
                  </button>
                ))}
              </div>
            ) : null}
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
            <label className="mt-4 flex items-start gap-2 text-sm font-semibold text-stone-800">
              <input
                className="mt-1 h-4 w-4 rounded border-stone-300 text-field-800"
                type="checkbox"
                checked={fiscalInvoiceRequested}
                onChange={(event) => setFiscalInvoiceRequested(event.target.checked)}
              />
              Cliente solicitou Nota Fiscal
            </label>
            {fiscalInvoiceRequested ? (
              <div className="mt-3 space-y-3 rounded-md border border-stone-200 bg-stone-50 p-3">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold text-stone-950">Dados para nota</h3>
                  <span className="rounded-md bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">NF Pendente</span>
                </div>
                <label className="block space-y-1">
                  <span className="label">CPF/CNPJ</span>
                  <input
                    className="form-field"
                    value={fiscalData.fiscal_document}
                    onChange={(event) => setFiscalData({ ...fiscalData, fiscal_document: event.target.value })}
                  />
                </label>
                <label className="block space-y-1">
                  <span className="label">Razao social / nome</span>
                  <input
                    className="form-field"
                    value={fiscalData.fiscal_name}
                    onChange={(event) => setFiscalData({ ...fiscalData, fiscal_name: event.target.value })}
                  />
                </label>
                <label className="block space-y-1">
                  <span className="label">Inscricao estadual</span>
                  <input
                    className="form-field"
                    value={fiscalData.fiscal_state_registration}
                    onChange={(event) => setFiscalData({ ...fiscalData, fiscal_state_registration: event.target.value })}
                  />
                </label>
                <label className="block space-y-1">
                  <span className="label">E-mail</span>
                  <input
                    className="form-field"
                    type="email"
                    value={fiscalData.fiscal_email}
                    onChange={(event) => setFiscalData({ ...fiscalData, fiscal_email: event.target.value })}
                  />
                </label>
              </div>
            ) : null}
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
