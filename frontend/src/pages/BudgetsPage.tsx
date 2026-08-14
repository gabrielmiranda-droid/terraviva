import { FileText } from "lucide-react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { WorkOrder } from "../types/domain";

async function fetchBudgetQueue() {
  const { data } = await api.get<WorkOrder[]>("/work-orders", { params: { status: "AGUARDANDO_APROVACAO" } });
  return data;
}

export function BudgetsPage() {
  const { data: workOrders = [], isLoading } = useQuery({ queryKey: ["budget-queue"], queryFn: fetchBudgetQueue });

  return (
    <div className="space-y-5">
      <PageHeader title="Orçamentos" />
      <div className="surface overflow-hidden">
        <table className="min-w-full divide-y divide-stone-200 text-sm">
          <thead className="table-head">
            <tr>
              <th className="table-cell">OS</th>
              <th className="table-cell">Status</th>
              <th className="table-cell">Problema</th>
              <th className="table-cell text-right">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {workOrders.map((workOrder) => (
              <tr key={workOrder.id} className="hover:bg-stone-50">
                <td className="table-cell font-semibold">
                  <Link className="hover:text-field-800" to={`/ordens-servico/${workOrder.id}`}>
                    {workOrder.number}
                  </Link>
                </td>
                <td className="table-cell">
                  <StatusBadge status={workOrder.status} />
                </td>
                <td className="table-cell text-stone-700">{workOrder.reported_problem}</td>
                <td className="table-cell text-right">R$ {Number(workOrder.total).toFixed(2)}</td>
              </tr>
            ))}
            {!isLoading && workOrders.length === 0 ? (
              <tr>
                <td className="p-6" colSpan={4}>
                  <EmptyState
                    icon={FileText}
                    title="Nenhum orçamento aguardando aprovação"
                    description="OS enviadas para aprovação do cliente aparecerão nesta fila."
                  />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
