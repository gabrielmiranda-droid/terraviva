import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { Customer, Machine, WorkOrder } from "../types/domain";
import { getStatusMeta } from "../utils/status";

const statusOptions = [
  "",
  "RECEBIDA",
  "AGUARDANDO_DIAGNOSTICO",
  "EM_DIAGNOSTICO",
  "AGUARDANDO_APROVACAO",
  "APROVADA",
  "RECUSADA",
  "AGUARDANDO_PECA",
  "EM_MANUTENCAO",
  "FINALIZADA",
  "PRONTA_PARA_ENTREGA",
  "ENTREGUE",
  "CANCELADA",
];

async function fetchWorkOrders(status: string) {
  const { data } = await api.get<WorkOrder[]>("/work-orders", { params: { status: status || undefined } });
  return data;
}

async function fetchCustomers() {
  const { data } = await api.get<Customer[]>("/customers");
  return data;
}

async function fetchMachines() {
  const { data } = await api.get<Machine[]>("/machines");
  return data;
}

export function WorkOrdersPage() {
  const [status, setStatus] = useState("");
  const { data: workOrders = [], isLoading } = useQuery({
    queryKey: ["work-orders", status],
    queryFn: () => fetchWorkOrders(status),
  });
  const { data: customers = [] } = useQuery({ queryKey: ["customers"], queryFn: fetchCustomers });
  const { data: machines = [] } = useQuery({ queryKey: ["machines"], queryFn: fetchMachines });
  const customerById = useMemo(() => new Map(customers.map((customer) => [customer.id, customer])), [customers]);
  const machineById = useMemo(() => new Map(machines.map((machine) => [machine.id, machine])), [machines]);

  return (
    <div className="space-y-5">
      <PageHeader title="Ordens de Servico" />

      <label className="flex max-w-sm flex-col gap-1">
        <span className="label">Status</span>
        <span className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={17} />
          <select className="form-field pl-9" value={status} onChange={(event) => setStatus(event.target.value)}>
            {statusOptions.map((option) => (
              <option key={option || "TODAS"} value={option}>
                {option ? getStatusMeta(option).label : "Todas"}
              </option>
            ))}
          </select>
        </span>
      </label>

      <div className="overflow-hidden rounded-md border border-stone-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="bg-stone-50 text-left text-xs font-semibold uppercase tracking-normal text-stone-600">
              <tr>
                <th className="px-4 py-3">Numero</th>
                <th className="px-4 py-3">Cliente</th>
                <th className="px-4 py-3">Maquina</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Problema</th>
                <th className="px-4 py-3">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {workOrders.map((workOrder) => {
                const customer = customerById.get(workOrder.customer_id);
                const machine = machineById.get(workOrder.machine_id);
                return (
                  <tr key={workOrder.id} className="hover:bg-stone-50">
                    <td className="px-4 py-3 font-semibold text-stone-950">
                      <Link className="hover:text-field-800" to={`/ordens-servico/${workOrder.id}`}>
                        {workOrder.number}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-stone-700">{customer?.name || "-"}</td>
                    <td className="px-4 py-3 text-stone-700">
                      {machine ? [machine.type, machine.brand, machine.model].filter(Boolean).join(" / ") : "-"}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={workOrder.status} />
                    </td>
                    <td className="max-w-md px-4 py-3 text-stone-700">{workOrder.reported_problem}</td>
                    <td className="px-4 py-3 text-stone-700">R$ {Number(workOrder.total).toFixed(2)}</td>
                  </tr>
                );
              })}
              {!isLoading && workOrders.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-stone-500" colSpan={6}>
                    Nenhuma OS encontrada.
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
