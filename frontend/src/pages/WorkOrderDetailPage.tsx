import { CheckCircle2, ClipboardList, FileText, Hammer, History, Images, PackagePlus, WalletCards, Wrench } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/Timeline";
import { api } from "../services/api";
import type { WorkOrderDetail } from "../types/domain";
import { getErrorMessage } from "../utils/errors";
import { formatAttendanceType, getStatusMeta } from "../utils/status";

const tabs = [
  { key: "resumo", label: "Resumo", icon: ClipboardList },
  { key: "diagnostico", label: "Diagnóstico", icon: Wrench },
  { key: "orcamento", label: "Orçamento", icon: FileText },
  { key: "servicos", label: "Serviços", icon: Hammer },
  { key: "pecas", label: "Peças utilizadas", icon: PackagePlus },
  { key: "fotos", label: "Fotos / Anexos", icon: Images },
  { key: "historico", label: "Histórico", icon: History },
  { key: "financeiro", label: "Financeiro", icon: WalletCards },
];

const nextStatusOptions = [
  "EM_DIAGNOSTICO",
  "AGUARDANDO_APROVACAO",
  "APROVADA",
  "EM_MANUTENCAO",
  "PRONTA_PARA_ENTREGA",
  "ENTREGUE",
  "RECUSADA",
];

async function fetchDetail(workOrderId?: string) {
  const { data } = await api.get<WorkOrderDetail>(`/work-orders/${workOrderId}/detail`);
  return data;
}

function machineLabel(detail: WorkOrderDetail) {
  return [detail.machine.type, detail.machine.brand, detail.machine.model].filter(Boolean).join(" / ");
}

export function WorkOrderDetailPage() {
  const { workOrderId } = useParams();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("resumo");
  const [diagnosis, setDiagnosis] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { data: detail, isLoading } = useQuery({
    queryKey: ["work-order-detail", workOrderId],
    queryFn: () => fetchDetail(workOrderId),
    enabled: Boolean(workOrderId),
  });

  useEffect(() => {
    if (detail) {
      setDiagnosis(detail.work_order.diagnosis || "");
    }
  }, [detail]);

  async function updateStatus(status: string) {
    if (!detail) return;
    setError(null);
    try {
      await api.patch(`/work-orders/${detail.work_order.id}/status`, {
        status,
        reason: reason || null,
        diagnosis: diagnosis || undefined,
      });
      setReason("");
      queryClient.invalidateQueries({ queryKey: ["work-order-detail", workOrderId] });
      queryClient.invalidateQueries({ queryKey: ["work-orders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-metrics"] });
      queryClient.invalidateQueries({ queryKey: ["workshop-flow"] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  if (isLoading) {
    return <p className="text-sm text-stone-600">Carregando OS...</p>;
  }

  if (!detail) {
    return <p className="text-sm text-stone-600">OS não encontrada.</p>;
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={`OS ${detail.work_order.number}`}
        actions={
          <Link className="btn-secondary" to="/ordens-servico">
            Voltar
          </Link>
        }
      />

      {error ? <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div> : null}

      <section className="surface p-4">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={detail.work_order.status} />
              <span className="rounded-md bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-700">
                Entrada {detail.entry.number}
              </span>
              <span className="rounded-md bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-700">
                {formatAttendanceType(detail.entry.attendance_type)}
              </span>
            </div>
            <h2 className="mt-3 text-xl font-bold text-stone-950">{detail.customer.name}</h2>
            <p className="text-sm text-stone-600">{machineLabel(detail)}</p>
            <p className="mt-2 max-w-3xl text-sm text-stone-700">{detail.work_order.reported_problem}</p>
          </div>

          <dl className="grid min-w-72 gap-2 text-sm">
            <div>
              <dt className="label">Data de entrada</dt>
              <dd className="font-medium">{new Date(detail.entry.entry_date).toLocaleString("pt-BR")}</dd>
            </div>
            <div>
              <dt className="label">Técnico</dt>
              <dd className="font-medium">{detail.work_order.technician_id || "Não definido"}</dd>
            </div>
            <div>
              <dt className="label">Total</dt>
              <dd className="font-medium">R$ {Number(detail.work_order.total).toFixed(2)}</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="surface overflow-hidden">
        <div className="flex gap-1 overflow-x-auto border-b border-stone-200 px-3 pt-3">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                className={[
                  "inline-flex min-h-10 items-center gap-2 rounded-t-md px-3 text-sm font-semibold transition",
                  activeTab === tab.key ? "bg-field-50 text-field-900" : "text-stone-600 hover:bg-stone-50",
                ].join(" ")}
                type="button"
                onClick={() => setActiveTab(tab.key)}
              >
                <Icon size={16} aria-hidden="true" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="p-4">
          {activeTab === "resumo" ? (
            <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
              <div>
                <h3 className="text-base font-semibold text-stone-950">Timeline da OS</h3>
                <div className="mt-4">
                  <Timeline
                    items={[
                      { status: "RECEBIDA", date: detail.entry.entry_date, reason: "Máquina recebida na oficina." },
                      ...detail.history.map((item) => ({
                        status: item.to_status,
                        date: item.changed_at,
                        reason: item.reason,
                      })),
                    ]}
                  />
                </div>
              </div>
              <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
                <h3 className="text-base font-semibold text-stone-950">Próxima ação</h3>
                <p className="mt-1 text-sm text-stone-600">{getStatusMeta(detail.work_order.status).description}</p>
                <label className="mt-4 block space-y-1">
                  <span className="label">Motivo / observação do status</span>
                  <textarea className="form-field min-h-20" value={reason} onChange={(event) => setReason(event.target.value)} />
                </label>
                <div className="mt-4 flex flex-wrap gap-2">
                  {nextStatusOptions.map((status) => (
                    <button className="btn-secondary" key={status} type="button" onClick={() => updateStatus(status)}>
                      {getStatusMeta(status).label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          {activeTab === "diagnostico" ? (
            <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
              <label className="block space-y-1">
                <span className="label">Diagnóstico técnico</span>
                <textarea
                  className="form-field min-h-52"
                  value={diagnosis}
                  onChange={(event) => setDiagnosis(event.target.value)}
                  placeholder="Registre a análise técnica, causa provável e orientação para orçamento ou execução."
                />
              </label>
              <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
                <h3 className="font-semibold text-stone-950">Ações</h3>
                <div className="mt-3 space-y-2">
                  <button className="btn-primary w-full" type="button" onClick={() => updateStatus("AGUARDANDO_APROVACAO")}>
                    <CheckCircle2 size={17} aria-hidden="true" />
                    Salvar e enviar para aprovação
                  </button>
                  <button className="btn-secondary w-full" type="button" onClick={() => updateStatus("EM_DIAGNOSTICO")}>
                    Manter em diagnóstico
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {activeTab === "orcamento" ? (
            <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
              <div className="rounded-md border border-dashed border-stone-300 bg-stone-50 p-5">
                <h3 className="font-semibold text-stone-950">Elaboração de orçamento</h3>
                <p className="mt-1 text-sm text-stone-600">
                  Estrutura preparada para peças e serviços. A próxima etapa técnica é persistir itens de orçamento e buscar peças do estoque.
                </p>
              </div>
              <div className="rounded-md border border-stone-200 bg-white p-4">
                <p className="text-sm text-stone-600">Total atual</p>
                <strong className="mt-2 block text-3xl text-stone-950">R$ {Number(detail.work_order.total).toFixed(2)}</strong>
              </div>
            </div>
          ) : null}

          {activeTab === "servicos" || activeTab === "pecas" || activeTab === "fotos" || activeTab === "financeiro" ? (
            <div className="rounded-md border border-stone-200 bg-stone-50 p-5">
              <h3 className="font-semibold text-stone-950">{tabs.find((tab) => tab.key === activeTab)?.label}</h3>
              <p className="mt-1 text-sm text-stone-600">
                Área reservada na central da OS para evolução sem misturar cadastro, orçamento, consumo real e financeiro.
              </p>
            </div>
          ) : null}

          {activeTab === "historico" ? (
            <Timeline items={detail.history.map((item) => ({ status: item.to_status, date: item.changed_at, reason: item.reason }))} />
          ) : null}
        </div>
      </section>
    </div>
  );
}
