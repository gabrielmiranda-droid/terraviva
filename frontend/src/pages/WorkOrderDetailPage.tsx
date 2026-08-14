import {
  CheckCircle2,
  ClipboardList,
  FileText,
  Hammer,
  History,
  Images,
  PackagePlus,
  Plus,
  Trash2,
  WalletCards,
  Wrench,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/Timeline";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { Budget, PartSearch, WorkOrderDetail } from "../types/domain";
import { getErrorMessage } from "../utils/errors";
import { formatAttendanceType, getStatusMeta } from "../utils/status";

const tabs = [
  { key: "resumo", label: "Resumo", icon: ClipboardList },
  { key: "diagnostico", label: "Diagnóstico", icon: Wrench },
  { key: "pecas", label: "Pecas", icon: PackagePlus },
  { key: "servicos", label: "Mao de obra", icon: Hammer },
  { key: "orcamento", label: "Lancar orcamento", icon: FileText },
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

function money(value?: string | number | null) {
  return Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

type BudgetDraftItem = {
  localId: string;
  id?: string;
  item_type: "PECA" | "SERVICO";
  part_id?: string | null;
  description: string;
  quantity: string;
  unit_price: string;
  discount: string;
  stock_available?: string | null;
  location?: string | null;
};

function itemTotal(item: BudgetDraftItem) {
  return Math.max(Number(item.quantity || 0) * Number(item.unit_price || 0) - Number(item.discount || 0), 0);
}

async function fetchBudget(workOrderId?: string) {
  const { data } = await api.get<Budget | null>(`/budgets/work-orders/${workOrderId}/budget`);
  return data;
}

async function fetchParts(search: string) {
  if (!search.trim()) return [];
  const { data } = await api.get<PartSearch[]>("/parts", { params: { search, limit: 20 } });
  return data;
}

function BudgetEditor({
  detail,
  setError,
}: {
  detail: WorkOrderDetail;
  setError: (message: string | null) => void;
}) {
  const queryClient = useQueryClient();
  const [partSearch, setPartSearch] = useState("");
  const debouncedPartSearch = useDebouncedValue(partSearch);
  const [items, setItems] = useState<BudgetDraftItem[]>([]);
  const [notes, setNotes] = useState("");
  const [discount, setDiscount] = useState("0");
  const [newService, setNewService] = useState({ description: "", quantity: "1", unit_price: "0", discount: "0" });
  const [newPartOpen, setNewPartOpen] = useState(false);
  const [newPart, setNewPart] = useState({
    legacy_code: "",
    internal_code: "",
    barcode: "",
    description: "",
    manufacturer: "",
    supplier_id: "",
    location: "",
    unit: "UN",
    cost_price: "0",
    sale_price: "0",
    current_stock: "0",
    minimum_stock: "0",
    notes: "",
  });
  const { data: budget, isLoading } = useQuery({
    queryKey: ["work-order-budget", detail.work_order.id],
    queryFn: () => fetchBudget(detail.work_order.id),
  });
  const { data: parts = [] } = useQuery({
    queryKey: ["parts", debouncedPartSearch],
    queryFn: () => fetchParts(debouncedPartSearch),
  });

  useEffect(() => {
    if (!budget) {
      setItems([]);
      setNotes("");
      setDiscount("0");
      return;
    }
    setItems(
      budget.items.map((item) => ({
        localId: item.id,
        id: item.id,
        item_type: item.item_type,
        part_id: item.part_id,
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
        discount: item.discount,
      })),
    );
    setNotes(budget.notes || "");
    setDiscount(budget.discount || "0");
  }, [budget]);

  async function createBudget() {
    setError(null);
    try {
      await api.post(`/budgets/work-orders/${detail.work_order.id}/budget`, {});
      queryClient.invalidateQueries({ queryKey: ["work-order-budget", detail.work_order.id] });
      queryClient.invalidateQueries({ queryKey: ["work-order-detail", detail.work_order.id] });
      queryClient.invalidateQueries({ queryKey: ["budget-queue"] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function addPart(part: PartSearch) {
    setItems((current) => [
      ...current,
      {
        localId: crypto.randomUUID(),
        item_type: "PECA",
        part_id: part.id,
        description: `${part.code || part.internal_code || ""} ${part.description}`.trim(),
        quantity: "1",
        unit_price: part.sale_price,
        discount: "0",
        stock_available: part.stock_available,
        location: part.location,
      },
    ]);
    setPartSearch("");
  }

  function addService() {
    if (!newService.description.trim() || Number(newService.quantity) <= 0) return;
    setItems((current) => [
      ...current,
      { localId: crypto.randomUUID(), item_type: "SERVICO", ...newService },
    ]);
    setNewService({ description: "", quantity: "1", unit_price: "0", discount: "0" });
  }

  async function saveBudget() {
    if (!budget) return;
    setError(null);
    try {
      await api.put(`/budgets/${budget.id}`, {
        date: budget.date,
        valid_until: budget.valid_until,
        notes: notes || null,
        discount,
        items: items.map((item) => ({
          id: item.id,
          item_type: item.item_type,
          part_id: item.part_id || null,
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
          discount: item.discount,
        })),
      });
      queryClient.invalidateQueries({ queryKey: ["work-order-budget", detail.work_order.id] });
      queryClient.invalidateQueries({ queryKey: ["work-order-detail", detail.work_order.id] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function transitionBudget(action: "finalize" | "approve" | "reject") {
    if (!budget) return;
    setError(null);
    try {
      if (action === "finalize") await saveBudget();
      await api.post(`/budgets/${budget.id}/${action}`, action === "reject" ? { reason: "Recusado pelo cliente." } : { method: "WhatsApp" });
      queryClient.invalidateQueries({ queryKey: ["work-order-budget", detail.work_order.id] });
      queryClient.invalidateQueries({ queryKey: ["work-order-detail", detail.work_order.id] });
      queryClient.invalidateQueries({ queryKey: ["budget-queue"] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function createPartAndAdd() {
    if (!newPart.description.trim()) {
      setError("Informe a descricao da peca.");
      return;
    }
    setError(null);
    try {
      const { data } = await api.post<PartSearch>("/parts", newPart);
      addPart(data);
      setNewPartOpen(false);
      setNewPart({
        legacy_code: "",
        internal_code: "",
        barcode: "",
        description: "",
        manufacturer: "",
        supplier_id: "",
        location: "",
        unit: "UN",
        cost_price: "0",
        sale_price: "0",
        current_stock: "0",
        minimum_stock: "0",
        notes: "",
      });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  const partsSubtotal = items.filter((item) => item.item_type === "PECA").reduce((sum, item) => sum + itemTotal(item), 0);
  const servicesSubtotal = items.filter((item) => item.item_type === "SERVICO").reduce((sum, item) => sum + itemTotal(item), 0);
  const total = Math.max(partsSubtotal + servicesSubtotal - Number(discount || 0), 0);

  if (isLoading) return <p className="text-sm text-stone-600">Carregando orcamento...</p>;

  if (!budget) {
    return (
      <div className="surface border-amber-200 bg-amber-50 p-5">
        <h3 className="text-base font-semibold text-amber-950">Esta maquina esta aguardando orcamento.</h3>
        <p className="mt-1 text-sm text-amber-800">Registre o diagnostico e monte pecas e servicos para enviar ao cliente.</p>
        <button className="btn-primary mt-4" type="button" onClick={createBudget}>
          <Plus size={17} aria-hidden="true" />
          Montar orcamento
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="surface grid gap-4 p-4 lg:grid-cols-[1fr_260px]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md bg-field-50 px-2 py-1 text-xs font-bold text-field-900">{budget.number}</span>
            <span className="rounded-md bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-700">{budget.status}</span>
          </div>
          <label className="mt-3 block space-y-1">
            <span className="label">Detalhes tecnicos / observacoes do orcamento</span>
            <textarea className="form-field min-h-24" value={notes} onChange={(event) => setNotes(event.target.value)} />
          </label>
        </div>
        <div className="rounded-md border border-field-200 bg-field-50 p-4">
          <p className="text-sm font-semibold text-field-900">Total do orcamento</p>
          <strong className="mt-2 block text-3xl text-stone-950">{money(total)}</strong>
          <p className="mt-2 text-xs text-stone-600">Pecas so baixam do estoque quando consumidas na OS.</p>
        </div>
      </div>

      <section className="surface p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-semibold text-stone-950">Pecas</h3>
          <button className="btn-secondary" type="button" onClick={() => setNewPartOpen((value) => !value)}>
            <Plus size={17} aria-hidden="true" />
            Cadastrar nova peca
          </button>
        </div>
        <div className="mt-3">
          <SearchField
            value={partSearch}
            onChange={setPartSearch}
            placeholder="Buscar por codigo, descricao, fabricante ou codigo de barras"
            ariaLabel="Buscar peca para orcamento"
          />
        </div>
        {parts.length > 0 ? (
          <div className="mt-3 grid gap-2">
            {parts.map((part) => (
              <button
                key={part.id}
                className="rounded-md border border-stone-200 bg-white p-3 text-left text-sm transition hover:border-field-700 hover:bg-field-50"
                type="button"
                onClick={() => addPart(part)}
              >
                <span className="font-semibold text-stone-950">{part.code || part.internal_code || "-"}</span>
                <span className="ml-2 text-stone-800">{part.description}</span>
                <span className="block text-xs text-stone-500">
                  Estoque: {Number(part.stock_available).toLocaleString("pt-BR")} | {part.location || "Sem local"} | {money(part.sale_price)}
                </span>
              </button>
            ))}
          </div>
        ) : null}
        {newPartOpen ? (
          <div className="mt-4 grid gap-3 rounded-md border border-stone-200 bg-stone-50 p-3 md:grid-cols-3">
            <input className="form-field" placeholder="Codigo" value={newPart.legacy_code} onChange={(event) => setNewPart({ ...newPart, legacy_code: event.target.value })} />
            <input className="form-field" placeholder="Codigo interno" value={newPart.internal_code} onChange={(event) => setNewPart({ ...newPart, internal_code: event.target.value })} />
            <input className="form-field" placeholder="Fabricante" value={newPart.manufacturer} onChange={(event) => setNewPart({ ...newPart, manufacturer: event.target.value })} />
            <input className="form-field md:col-span-2" placeholder="Descricao" value={newPart.description} onChange={(event) => setNewPart({ ...newPart, description: event.target.value })} />
            <input className="form-field" placeholder="Localizacao" value={newPart.location} onChange={(event) => setNewPart({ ...newPart, location: event.target.value })} />
            <input className="form-field" placeholder="Unidade" value={newPart.unit} onChange={(event) => setNewPart({ ...newPart, unit: event.target.value })} />
            <input className="form-field" placeholder="Preco custo" type="number" min="0" step="0.01" value={newPart.cost_price} onChange={(event) => setNewPart({ ...newPart, cost_price: event.target.value })} />
            <input className="form-field" placeholder="Preco venda" type="number" min="0" step="0.01" value={newPart.sale_price} onChange={(event) => setNewPart({ ...newPart, sale_price: event.target.value })} />
            <input className="form-field" placeholder="Estoque atual" type="number" min="0" step="0.001" value={newPart.current_stock} onChange={(event) => setNewPart({ ...newPart, current_stock: event.target.value })} />
            <input className="form-field" placeholder="Estoque minimo" type="number" min="0" step="0.001" value={newPart.minimum_stock} onChange={(event) => setNewPart({ ...newPart, minimum_stock: event.target.value })} />
            <input className="form-field md:col-span-2" placeholder="Observacoes" value={newPart.notes} onChange={(event) => setNewPart({ ...newPart, notes: event.target.value })} />
            <button className="btn-primary md:col-span-3" type="button" onClick={createPartAndAdd}>
              Salvar peca e adicionar
            </button>
          </div>
        ) : null}
      </section>

      <section className="surface p-4">
        <h3 className="font-semibold text-stone-950">Servicos / mao de obra</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-[1fr_110px_140px_140px_auto]">
          <input className="form-field" placeholder="Descricao do servico" value={newService.description} onChange={(event) => setNewService({ ...newService, description: event.target.value })} />
          <input className="form-field" type="number" min="0.001" step="0.001" value={newService.quantity} onChange={(event) => setNewService({ ...newService, quantity: event.target.value })} />
          <input className="form-field" type="number" min="0" step="0.01" value={newService.unit_price} onChange={(event) => setNewService({ ...newService, unit_price: event.target.value })} />
          <input className="form-field" type="number" min="0" step="0.01" value={newService.discount} onChange={(event) => setNewService({ ...newService, discount: event.target.value })} />
          <button className="btn-secondary" type="button" onClick={addService}>Adicionar</button>
        </div>
      </section>

      <section className="surface overflow-hidden">
        <table className="min-w-full divide-y divide-stone-200 text-sm">
          <thead className="table-head">
            <tr>
              <th className="table-cell">Tipo</th>
              <th className="table-cell">Descricao</th>
              <th className="table-cell text-right">Qtd</th>
              <th className="table-cell">Estoque</th>
              <th className="table-cell text-right">Unitario</th>
              <th className="table-cell text-right">Total</th>
              <th className="table-cell text-right">Acoes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {items.map((item) => (
              <tr key={item.localId}>
                <td className="table-cell">{item.item_type === "PECA" ? "Peca" : "Servico"}</td>
                <td className="table-cell">{item.description}</td>
                <td className="table-cell text-right">
                  <input className="form-field w-24 text-right" type="number" min="0.001" step="0.001" value={item.quantity} onChange={(event) => setItems((current) => current.map((row) => row.localId === item.localId ? { ...row, quantity: event.target.value } : row))} />
                </td>
                <td className="table-cell">
                  {item.item_type === "PECA" ? (
                    Number(item.stock_available ?? 0) <= 0 ? <span className="rounded-md bg-amber-100 px-2 py-1 text-xs font-bold text-amber-900">Sem estoque</span> : Number(item.stock_available).toLocaleString("pt-BR")
                  ) : "-"}
                  {item.location ? <span className="block text-xs text-stone-500">{item.location}</span> : null}
                </td>
                <td className="table-cell text-right">{money(item.unit_price)}</td>
                <td className="table-cell text-right font-semibold">{money(itemTotal(item))}</td>
                <td className="table-cell text-right">
                  <button className="icon-button" type="button" onClick={() => setItems((current) => current.filter((row) => row.localId !== item.localId))}>
                    <Trash2 size={15} aria-hidden="true" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="surface grid gap-3 p-4 md:grid-cols-[1fr_180px_220px] md:items-end">
        <label className="block space-y-1 md:col-start-2">
          <span className="label">Desconto geral</span>
          <input className="form-field text-right" type="number" min="0" step="0.01" value={discount} onChange={(event) => setDiscount(event.target.value)} />
        </label>
        <div className="rounded-md bg-stone-950 p-4 text-white">
          <p className="text-xs font-semibold uppercase">Total</p>
          <strong className="mt-1 block text-2xl">{money(total)}</strong>
        </div>
        <div className="flex flex-wrap gap-2 md:col-span-3 md:justify-end">
          <button className="btn-secondary" type="button" onClick={saveBudget}>Salvar rascunho</button>
          <button className="btn-primary" type="button" onClick={() => transitionBudget("finalize")}>Lancar em Orcamentos</button>
          <button className="btn-secondary" type="button" onClick={() => window.print()}>Imprimir</button>
          <button className="btn-secondary" type="button" onClick={() => transitionBudget("approve")}>Registrar aprovacao</button>
          <button className="btn-secondary" type="button" onClick={() => transitionBudget("reject")}>Registrar recusa</button>
        </div>
      </section>
    </div>
  );
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

  async function updateStatus(status: string, nextTab?: string) {
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
      if (nextTab) setActiveTab(nextTab);
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
                  <button className="btn-primary" type="button" onClick={() => setActiveTab("pecas")}>
                    <PackagePlus size={17} aria-hidden="true" />
                    Adicionar pecas
                  </button>
                  <button className="btn-secondary" type="button" onClick={() => setActiveTab("servicos")}>
                    <Hammer size={17} aria-hidden="true" />
                    Adicionar mao de obra
                  </button>
                  <button className="btn-secondary" type="button" onClick={() => setActiveTab("orcamento")}>
                    <FileText size={17} aria-hidden="true" />
                    Lancar em Orcamentos
                  </button>
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
                  <button className="btn-primary w-full" type="button" onClick={() => updateStatus("AGUARDANDO_ORCAMENTO", "pecas")}>
                    <CheckCircle2 size={17} aria-hidden="true" />
                    Salvar diagnostico e montar orcamento
                  </button>
                  <button className="btn-secondary w-full" type="button" onClick={() => updateStatus("EM_DIAGNOSTICO")}>
                    Manter em diagnóstico
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {["orcamento", "pecas", "servicos"].includes(activeTab) ? (
            <BudgetEditor detail={detail} setError={setError} />
          ) : null}

          {activeTab === "fotos" || activeTab === "financeiro" ? (
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
