import { CheckCircle2, Tractor } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { StatusBadge } from "../components/StatusBadge";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { WorkshopMachine } from "../types/domain";
import { getErrorMessage } from "../utils/errors";
import { formatAttendanceType, getStatusMeta } from "../utils/status";

const statusOptions = [
  "",
  "RECEBIDA",
  "AGUARDANDO_DIAGNOSTICO",
  "EM_DIAGNOSTICO",
  "AGUARDANDO_APROVACAO",
  "APROVADA",
  "AGUARDANDO_PECA",
  "EM_MANUTENCAO",
  "FINALIZADA",
  "PRONTA_PARA_ENTREGA",
];

async function fetchMachinesInShop(search: string, status: string, attendanceType: string) {
  const { data } = await api.get<WorkshopMachine[]>("/machine-entries/in-shop", {
    params: {
      search: search || undefined,
      status: status || undefined,
      attendance_type: attendanceType || undefined,
      limit: 200,
    },
  });
  return data;
}

export function MachinesInShopPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const [status, setStatus] = useState("");
  const [attendanceType, setAttendanceType] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { data: machines = [], isLoading } = useQuery({
    queryKey: ["machines-in-shop", debouncedSearch, status, attendanceType],
    queryFn: () => fetchMachinesInShop(debouncedSearch, status, attendanceType),
  });

  async function markDelivered(entryId: string) {
    setError(null);
    try {
      await api.post(`/machine-entries/${entryId}/deliver`, {});
      queryClient.invalidateQueries({ queryKey: ["machines-in-shop"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-metrics"] });
      queryClient.invalidateQueries({ queryKey: ["workshop-flow"] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title="Máquinas na Oficina"
        actions={
          <Link className="btn-primary" to="/entrada">
            Nova Entrada
          </Link>
        }
      />

      {error ? <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div> : null}

      <section className="surface grid gap-3 p-4 md:grid-cols-[1fr_220px_220px]">
        <SearchField
          value={search}
          onChange={setSearch}
          placeholder="Buscar por cliente, OS, entrada, serie ou maquina"
          ariaLabel="Buscar maquinas na oficina"
        />
        <select className="form-field" value={status} onChange={(event) => setStatus(event.target.value)}>
          {statusOptions.map((option) => (
            <option key={option || "TODAS"} value={option}>
              {option ? getStatusMeta(option).label : "Todos os status"}
            </option>
          ))}
        </select>
        <select className="form-field" value={attendanceType} onChange={(event) => setAttendanceType(event.target.value)}>
          <option value="">Todos atendimentos</option>
          <option value="SERVICO_DIRETO">Executar serviço</option>
          <option value="ORCAMENTO">Fazer orçamento</option>
        </select>
      </section>

      <div className="surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="table-head">
              <tr>
                <th className="table-cell">Entrada / OS</th>
                <th className="table-cell">Cliente</th>
                <th className="table-cell">Máquina</th>
                <th className="table-cell">Status</th>
                <th className="table-cell">Atendimento</th>
                <th className="table-cell">Tempo</th>
                <th className="table-cell text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {machines.map((item) => (
                <tr key={item.entry_id} className={item.days_in_shop >= 5 ? "bg-amber-50/70" : "hover:bg-stone-50"}>
                  <td className="table-cell">
                    <Link className="font-bold text-stone-950 hover:text-field-800" to={`/ordens-servico/${item.work_order_id}`}>
                      {item.entry_number}
                    </Link>
                    <span className="block text-xs text-stone-500">{item.work_order_number}</span>
                  </td>
                  <td className="table-cell">
                    <p className="font-medium text-stone-950">{item.customer_name}</p>
                    <p className="text-xs text-stone-500">{item.customer_phone || "-"}</p>
                  </td>
                  <td className="table-cell">
                    <p className="font-medium text-stone-950">
                      {[item.machine_type, item.machine_brand, item.machine_model].filter(Boolean).join(" / ")}
                    </p>
                    <p className="text-xs text-stone-500">Série: {item.machine_serial_number || "-"}</p>
                  </td>
                  <td className="table-cell">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="table-cell text-stone-700">{formatAttendanceType(item.attendance_type)}</td>
                  <td className="table-cell">
                    <span className={item.days_in_shop >= 5 ? "font-bold text-amber-800" : "text-stone-700"}>
                      há {item.days_in_shop} dia{item.days_in_shop === 1 ? "" : "s"}
                    </span>
                    <span className="block text-xs text-stone-500">
                      {new Date(item.entered_at).toLocaleDateString("pt-BR")}
                    </span>
                  </td>
                  <td className="table-cell text-right">
                    <button className="btn-secondary" type="button" onClick={() => markDelivered(item.entry_id)}>
                      <CheckCircle2 size={17} aria-hidden="true" />
                      Entregar
                    </button>
                  </td>
                </tr>
              ))}
              {!isLoading && machines.length === 0 ? (
                <tr>
                  <td className="px-4 py-8" colSpan={7}>
                    <EmptyState
                      icon={Tractor}
                      title="Nenhuma máquina na oficina"
                      description="Entradas ainda não entregues aparecerão aqui automaticamente."
                      action={
                        <Link className="btn-primary" to="/entrada">
                          Nova Entrada
                        </Link>
                      }
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
