import { Plus, Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { Customer } from "../types/domain";

async function fetchCustomers(search: string) {
  const { data } = await api.get<Customer[]>("/customers", { params: { search: search || undefined } });
  return data;
}

export function CustomersPage() {
  const [search, setSearch] = useState("");
  const [submittedSearch, setSubmittedSearch] = useState("");
  const { data = [], isLoading } = useQuery({
    queryKey: ["customers", submittedSearch],
    queryFn: () => fetchCustomers(submittedSearch),
  });

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    setSubmittedSearch(search);
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title="Clientes"
        actions={
          <Link className="btn-primary" to="/clientes/novo">
            <Plus size={17} aria-hidden="true" />
            Novo cliente
          </Link>
        }
      />

      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={handleSearch}>
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={17} />
          <input
            className="form-field pl-9"
            placeholder="Buscar por nome, documento, telefone ou email"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <button className="btn-secondary" type="submit">
          <Search size={17} aria-hidden="true" />
          Buscar
        </button>
      </form>

      <div className="overflow-hidden rounded-md border border-stone-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="bg-stone-50 text-left text-xs font-semibold uppercase tracking-normal text-stone-600">
              <tr>
                <th className="px-4 py-3">Nome</th>
                <th className="px-4 py-3">Documento</th>
                <th className="px-4 py-3">WhatsApp</th>
                <th className="px-4 py-3">Cidade</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {data.map((customer) => (
                <tr key={customer.id} className="hover:bg-stone-50">
                  <td className="px-4 py-3 font-medium text-stone-950">
                    <Link className="hover:text-field-800" to={`/clientes/${customer.id}`}>
                      {customer.name}
                    </Link>
                    {customer.trade_name ? (
                      <span className="block text-xs font-normal text-stone-500">{customer.trade_name}</span>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 text-stone-700">{customer.document || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">{customer.whatsapp || customer.phone || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">
                    {[customer.city, customer.state].filter(Boolean).join(" / ") || "-"}
                  </td>
                  <td className="px-4 py-3 text-stone-700">{customer.is_active ? "Ativo" : "Inativo"}</td>
                </tr>
              ))}
              {!isLoading && data.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-stone-500" colSpan={5}>
                    Nenhum cliente encontrado.
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
