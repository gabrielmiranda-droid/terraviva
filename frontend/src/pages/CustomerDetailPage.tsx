import { Plus, Tractor } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { Customer, Machine } from "../types/domain";

async function fetchCustomer(customerId: string) {
  const { data } = await api.get<Customer>(`/customers/${customerId}`);
  return data;
}

async function fetchMachines(customerId: string) {
  const { data } = await api.get<Machine[]>("/machines", { params: { customer_id: customerId } });
  return data;
}

export function CustomerDetailPage() {
  const { customerId = "" } = useParams();
  const { data: customer, isLoading } = useQuery({
    queryKey: ["customer", customerId],
    queryFn: () => fetchCustomer(customerId),
    enabled: Boolean(customerId),
  });
  const { data: machines = [] } = useQuery({
    queryKey: ["machines", customerId],
    queryFn: () => fetchMachines(customerId),
    enabled: Boolean(customerId),
  });

  if (isLoading) {
    return <p className="text-sm text-stone-600">Carregando...</p>;
  }

  if (!customer) {
    return <p className="text-sm text-stone-600">Cliente nao encontrado.</p>;
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={customer.name}
        actions={
          <Link className="btn-primary" to={`/maquinas/nova?customer_id=${customer.id}`}>
            <Plus size={17} aria-hidden="true" />
            Nova maquina
          </Link>
        }
      />

      <section className="grid gap-4 rounded-md border border-stone-200 bg-white p-4 shadow-sm md:grid-cols-3">
        <div>
          <span className="label">Documento</span>
          <p className="mt-1 text-sm text-stone-900">{customer.document || "-"}</p>
        </div>
        <div>
          <span className="label">WhatsApp</span>
          <p className="mt-1 text-sm text-stone-900">{customer.whatsapp || customer.phone || "-"}</p>
        </div>
        <div>
          <span className="label">Email</span>
          <p className="mt-1 text-sm text-stone-900">{customer.email || "-"}</p>
        </div>
        <div className="md:col-span-3">
          <span className="label">Endereco</span>
          <p className="mt-1 text-sm text-stone-900">
            {[customer.address, customer.number, customer.district, customer.city, customer.state]
              .filter(Boolean)
              .join(", ") || "-"}
          </p>
        </div>
      </section>

      <section className="rounded-md border border-stone-200 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-stone-200 px-4 py-3">
          <Tractor size={18} className="text-field-800" aria-hidden="true" />
          <h2 className="text-base font-semibold tracking-normal text-stone-950">Maquinas</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="bg-stone-50 text-left text-xs font-semibold uppercase tracking-normal text-stone-600">
              <tr>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Marca</th>
                <th className="px-4 py-3">Modelo</th>
                <th className="px-4 py-3">Identificacao</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {machines.map((machine) => (
                <tr key={machine.id}>
                  <td className="px-4 py-3 font-medium text-stone-950">{machine.type}</td>
                  <td className="px-4 py-3 text-stone-700">{machine.brand || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">{machine.model || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">{machine.identification || machine.serial_number || "-"}</td>
                </tr>
              ))}
              {machines.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-stone-500" colSpan={4}>
                    Nenhuma maquina cadastrada.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
