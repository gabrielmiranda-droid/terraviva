import { FileText } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { StatusBadge } from "../components/StatusBadge";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { WorkshopMachine } from "../types/domain";
import { getStatusMeta } from "../utils/status";

const statusOptions = [
  "",
  "AGUARDANDO_DIAGNOSTICO",
  "EM_DIAGNOSTICO",
  "AGUARDANDO_ORCAMENTO",
  "AGUARDANDO_APROVACAO",
  "APROVADA",
  "RECUSADA",
];

async function fetchBudgetQueue(search: string, status: string) {
  const { data } = await api.get<WorkshopMachine[]>("/budgets/pending", {
    params: { search: search || undefined, status: status || undefined, limit: 200 },
  });
  return data;
}

export function BudgetsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data: items = [], isLoading } = useQuery({
    queryKey: ["budget-queue", debouncedSearch, status],
    queryFn: () => fetchBudgetQueue(debouncedSearch, status),
  });

  return (
    <div className="space-y-5">
      <PageHeader title="Orcamentos" />

      <section className="surface grid gap-3 p-4 md:grid-cols-[1fr_260px]">
        <SearchField
          value={search}
          onChange={setSearch}
          placeholder="Buscar por cliente, OS, entrada, documento ou maquina"
          ariaLabel="Buscar fila de orcamentos"
        />
        <select className="form-field" value={status} onChange={(event) => setStatus(event.target.value)}>
          {statusOptions.map((option) => (
            <option key={option || "TODOS"} value={option}>
              {option ? getStatusMeta(option).label : "Todos os status"}
            </option>
          ))}
        </select>
      </section>

      <div className="surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="table-head">
              <tr>
                <th className="table-cell">Entrada / OS</th>
                <th className="table-cell">Cliente</th>
                <th className="table-cell">Maquina</th>
                <th className="table-cell">Entrada</th>
                <th className="table-cell">Status</th>
                <th className="table-cell">Problema</th>
                <th className="table-cell">Tempo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {items.map((item) => (
                <tr key={item.work_order_id} className="hover:bg-stone-50">
                  <td className="table-cell font-semibold">
                    <Link className="hover:text-field-800" to={`/ordens-servico/${item.work_order_id}`}>
                      {item.entry_number}
                    </Link>
                    <span className="block text-xs font-normal text-stone-500">{item.work_order_number}</span>
                  </td>
                  <td className="table-cell text-stone-800">{item.customer_name}</td>
                  <td className="table-cell text-stone-700">
                    {[item.machine_type, item.machine_brand, item.machine_model].filter(Boolean).join(" / ") || "-"}
                    <span className="block text-xs text-stone-500">Serie: {item.machine_serial_number || "-"}</span>
                  </td>
                  <td className="table-cell text-stone-700">
                    {new Date(item.entered_at).toLocaleDateString("pt-BR")}
                  </td>
                  <td className="table-cell">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="table-cell max-w-md text-stone-700">{item.reported_problem}</td>
                  <td className="table-cell text-stone-700">
                    ha {item.days_in_shop} dia{item.days_in_shop === 1 ? "" : "s"}
                    <span className="block text-xs text-stone-500">{item.technician_name || "Sem tecnico"}</span>
                  </td>
                </tr>
              ))}
              {!isLoading && items.length === 0 ? (
                <tr>
                  <td className="p-6" colSpan={7}>
                    <EmptyState
                      icon={FileText}
                      title="Nenhuma maquina aguardando orcamento"
                      description="Entradas marcadas como orcamento aparecerao aqui automaticamente."
                    />
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
