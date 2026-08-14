import { ClipboardCheck, ClipboardList, Clock, Hammer, PackageCheck, Tractor, Wrench } from "lucide-react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { DashboardMetrics, DatabaseStatus, WorkshopFlow } from "../types/domain";

async function fetchMetrics() {
  const { data } = await api.get<DashboardMetrics>("/dashboard/metrics");
  return data;
}

async function fetchDatabaseStatus() {
  const { data } = await api.get<DatabaseStatus>("/dashboard/database");
  return data;
}

async function fetchWorkshopFlow() {
  const { data } = await api.get<WorkshopFlow>("/dashboard/workshop-flow");
  return data;
}

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard-metrics"], queryFn: fetchMetrics });
  const { data: databaseStatus } = useQuery({
    queryKey: ["database-status"],
    queryFn: fetchDatabaseStatus,
  });
  const { data: flow } = useQuery({ queryKey: ["workshop-flow"], queryFn: fetchWorkshopFlow });
  const metrics = data ?? {
    machines_in_shop: 0,
    entries_today: 0,
    open_work_orders: 0,
    waiting_diagnosis: 0,
    waiting_approval: 0,
    in_maintenance: 0,
    ready_for_pickup: 0,
  };

  return (
    <div className="space-y-5">
      <PageHeader
        title="Dashboard"
        actions={
          <Link className="btn-primary" to="/entrada">
            Nova Entrada
          </Link>
        }
      />

      {databaseStatus && !databaseStatus.is_supabase ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {databaseStatus.message}
        </div>
      ) : null}

      {isLoading ? <p className="text-sm text-stone-600">Carregando...</p> : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Máquinas na oficina" value={metrics.machines_in_shop} icon={Tractor} />
        <MetricCard title="Entradas hoje" value={metrics.entries_today} icon={Clock} />
        <MetricCard title="OS abertas" value={metrics.open_work_orders} icon={ClipboardList} />
        <MetricCard title="Aguardando diagnóstico" value={metrics.waiting_diagnosis} icon={Wrench} />
        <MetricCard title="Aguardando aprovação" value={metrics.waiting_approval} icon={ClipboardCheck} />
        <MetricCard title="Em manutenção" value={metrics.in_maintenance} icon={Hammer} />
        <MetricCard title="Prontas para retirada" value={metrics.ready_for_pickup} icon={PackageCheck} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="surface p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-stone-950">Fluxo da Oficina</h2>
              <p className="text-sm text-stone-600">Onde cada máquina está parada agora.</p>
            </div>
            <Link className="btn-secondary" to="/oficina">
              Ver oficina
            </Link>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-5">
            {(flow?.columns ?? []).map((column) => (
              <div key={column.key} className="rounded-md border border-stone-200 bg-stone-50 p-3">
                <p className="min-h-10 text-xs font-bold uppercase tracking-normal text-stone-500">{column.label}</p>
                <strong className="mt-2 block text-3xl font-semibold text-stone-950">{column.count}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="surface p-4">
          <h2 className="text-base font-semibold text-stone-950">Precisam de atenção</h2>
          <p className="text-sm text-stone-600">Máquinas há mais tempo dentro da oficina.</p>
          <div className="mt-4 space-y-3">
            {flow?.attention?.length ? (
              flow.attention.map((item) => (
                <Link
                  key={item.work_order_id}
                  className={[
                    "block rounded-md border p-3 transition hover:border-field-700 hover:bg-field-50",
                    item.days_in_shop >= 5 ? "border-amber-300 bg-amber-50" : "border-stone-200 bg-white",
                  ].join(" ")}
                  to={`/ordens-servico/${item.work_order_id}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-stone-950">
                        {item.entry_number} · {item.customer_name}
                      </p>
                      <p className="text-sm text-stone-600">{item.machine_label}</p>
                    </div>
                    <span className="shrink-0 text-xs font-semibold text-stone-500">
                      há {item.days_in_shop} dia{item.days_in_shop === 1 ? "" : "s"}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <StatusBadge status={item.status} />
                    <p className="line-clamp-1 text-xs text-stone-500">{item.reported_problem}</p>
                  </div>
                </Link>
              ))
            ) : (
              <EmptyState
                icon={Tractor}
                title="Nenhuma pendência operacional"
                description="Quando houver máquinas aguardando diagnóstico, aprovação ou manutenção, elas aparecerão aqui."
              />
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
