import {
  BadgeCheck,
  CheckCircle2,
  ClipboardList,
  FileText,
  Plus,
  Printer,
  Search,
  Tractor,
  UserRoundPlus,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { CustomerEntryReceipt, MachineTag } from "../components/PrintDocuments";
import { EmptyState } from "../components/EmptyState";
import { Modal } from "../components/Modal";
import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { Stepper } from "../components/Stepper";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { AttendanceType, Customer, Machine, MachineEntryResult } from "../types/domain";
import { getErrorMessage } from "../utils/errors";
import { formatAttendanceType } from "../utils/status";

const steps = ["Cliente", "Máquina", "Recebimento", "Atendimento"];
const accessoryOptions = ["bateria", "carregador", "lâmina", "corrente", "sabre", "protetor", "chave", "outros"];

type CustomerDraft = {
  name: string;
  trade_name: string;
  document: string;
  phone: string;
  whatsapp: string;
  email: string;
  zip_code: string;
  address: string;
  number: string;
  district: string;
  city: string;
  state: string;
  notes: string;
};

type MachineDraft = {
  type: string;
  brand: string;
  model: string;
  serial_number: string;
  identification: string;
};

async function fetchCustomers(search: string) {
  const { data } = await api.get<Customer[]>("/customers", {
    params: { search: search || undefined, limit: 50 },
  });
  return data;
}

async function fetchMachines(customerId?: string) {
  if (!customerId) return [];
  const { data } = await api.get<Machine[]>("/machines", { params: { customer_id: customerId, limit: 100 } });
  return data;
}

function machineLabel(machine: Machine) {
  return [machine.type, machine.brand, machine.model].filter(Boolean).join(" / ");
}

const emptyCustomerDraft: CustomerDraft = {
  name: "",
  trade_name: "",
  document: "",
  phone: "",
  whatsapp: "",
  email: "",
  zip_code: "",
  address: "",
  number: "",
  district: "",
  city: "",
  state: "",
  notes: "",
};

function customerDraftFromSearch(search: string): CustomerDraft {
  const draft = { ...emptyCustomerDraft };
  const value = search.trim();
  if (!value) return draft;

  const digits = value.replace(/\D/g, "");
  if (value.includes("@")) {
    draft.email = value;
  } else if (digits.length >= 11) {
    draft.document = digits;
  } else if (digits.length >= 8) {
    draft.phone = digits;
    draft.whatsapp = digits;
  } else {
    draft.name = value;
  }
  return draft;
}

export function MachineEntryPage() {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(0);
  const [customerSearch, setCustomerSearch] = useState("");
  const debouncedCustomerSearch = useDebouncedValue(customerSearch);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [reportedProblem, setReportedProblem] = useState("");
  const [visualCondition, setVisualCondition] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedAccessories, setSelectedAccessories] = useState<string[]>([]);
  const [accessoryNotes, setAccessoryNotes] = useState("");
  const [attendanceType, setAttendanceType] = useState<AttendanceType>("SERVICO_DIRETO");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<MachineEntryResult | null>(null);
  const [customerModalOpen, setCustomerModalOpen] = useState(false);
  const [machineModalOpen, setMachineModalOpen] = useState(false);
  const [customerDraft, setCustomerDraft] = useState<CustomerDraft>(emptyCustomerDraft);
  const [machineDraft, setMachineDraft] = useState<MachineDraft>({
    type: "",
    brand: "",
    model: "",
    serial_number: "",
    identification: "",
  });
  const [printMode, setPrintMode] = useState<"receipt" | "tag" | null>(null);

  const { data: customers = [], isLoading: loadingCustomers } = useQuery({
    queryKey: ["customers", debouncedCustomerSearch],
    queryFn: () => fetchCustomers(debouncedCustomerSearch),
  });
  const { data: machines = [], isLoading: loadingMachines } = useQuery({
    queryKey: ["machines", selectedCustomer?.id],
    queryFn: () => fetchMachines(selectedCustomer?.id),
  });

  const accessories = useMemo(() => {
    return [...selectedAccessories, accessoryNotes.trim()].filter(Boolean).join(", ");
  }, [accessoryNotes, selectedAccessories]);

  function toggleAccessory(option: string) {
    setSelectedAccessories((current) =>
      current.includes(option) ? current.filter((item) => item !== option) : [...current, option],
    );
  }

  function openCustomerModal() {
    setCustomerDraft((current) => {
      const hasDraft = Object.values(current).some((value) => value.trim());
      return hasDraft ? current : customerDraftFromSearch(customerSearch);
    });
    setCustomerModalOpen(true);
  }

  async function createCustomer(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (customerDraft.name.trim().length < 2) {
      setError("Informe o nome do cliente para continuar a entrada.");
      return;
    }
    try {
      const payload = Object.fromEntries(
        Object.entries(customerDraft).map(([key, value]) => [key, value.trim() || null]),
      );
      const { data } = await api.post<Customer>("/customers", payload);
      setSelectedCustomer(data);
      setCustomerSearch(data.name);
      setCustomerDraft(emptyCustomerDraft);
      setCustomerModalOpen(false);
      setStep(1);
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function createMachine(event: FormEvent) {
    event.preventDefault();
    if (!selectedCustomer) return;
    setError(null);
    try {
      const payload = {
        customer_id: selectedCustomer.id,
        ...Object.fromEntries(Object.entries(machineDraft).map(([key, value]) => [key, value.trim() || null])),
      };
      const { data } = await api.post<Machine>("/machines", payload);
      setSelectedMachine(data);
      setMachineModalOpen(false);
      setStep(2);
      queryClient.invalidateQueries({ queryKey: ["machines", selectedCustomer.id] });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function submitEntry() {
    if (!selectedCustomer || !selectedMachine || reportedProblem.trim().length < 3) {
      setError("Selecione cliente, máquina e informe o problema relatado.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const { data } = await api.post<MachineEntryResult>("/machine-entries", {
        customer_id: selectedCustomer.id,
        machine_id: selectedMachine.id,
        attendance_type: attendanceType,
        reported_problem: reportedProblem,
        accessories: accessories || null,
        visual_condition: visualCondition || null,
        notes: notes || null,
      });
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ["dashboard-metrics"] });
      queryClient.invalidateQueries({ queryKey: ["workshop-flow"] });
      queryClient.invalidateQueries({ queryKey: ["machines-in-shop"] });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function printDocument(mode: "receipt" | "tag") {
    if (!result) return;
    await api.post(`/machine-entries/${result.entry.id}/print-jobs`, {
      document_type: mode === "receipt" ? "CUSTOMER_ENTRY_RECEIPT" : "MACHINE_TAG",
    });
    setPrintMode(mode);
    window.setTimeout(() => window.print(), 250);
  }

  function resetFlow() {
    setStep(0);
    setSelectedCustomer(null);
    setSelectedMachine(null);
    setReportedProblem("");
    setVisualCondition("");
    setNotes("");
    setSelectedAccessories([]);
    setAccessoryNotes("");
    setAttendanceType("SERVICO_DIRETO");
    setCustomerDraft(emptyCustomerDraft);
    setMachineDraft({
      type: "",
      brand: "",
      model: "",
      serial_number: "",
      identification: "",
    });
    setResult(null);
    setError(null);
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Nova Entrada" />

      <Stepper steps={steps} current={step} />

      {error ? <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div> : null}

      <section className={step === 0 ? "space-y-4" : "hidden"}>
        <div className="surface grid gap-3 p-4 md:grid-cols-[1fr_auto]">
          <SearchField
            value={customerSearch}
            onChange={setCustomerSearch}
            placeholder="Buscar por nome, telefone, WhatsApp, CPF ou CNPJ"
            ariaLabel="Buscar cliente para entrada"
          />
          <button className="btn-primary" type="button" onClick={openCustomerModal}>
            <Plus size={17} aria-hidden="true" />
            Novo cliente
          </button>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          {customers.map((customer) => (
            <button
              key={customer.id}
              className={[
                "rounded-md border bg-white p-4 text-left shadow-sm transition hover:border-field-700 hover:bg-field-50",
                selectedCustomer?.id === customer.id ? "border-field-700 ring-2 ring-field-100" : "border-stone-200",
              ].join(" ")}
              type="button"
              onClick={() => {
                setSelectedCustomer(customer);
                setSelectedMachine(null);
                setStep(1);
              }}
            >
              <p className="font-semibold text-stone-950">{customer.name}</p>
              <p className="mt-1 text-sm text-stone-600">{customer.whatsapp || customer.phone || "Sem telefone"}</p>
              <p className="text-xs text-stone-500">{customer.document || "Documento não informado"}</p>
            </button>
          ))}
        </div>

        {!loadingCustomers && customers.length === 0 ? (
          <EmptyState
            icon={UserRoundPlus}
            title="Nenhum cliente encontrado"
            description="Cadastre o cliente sem sair do fluxo de entrada."
            action={null}
          />
        ) : null}
      </section>

      <section className={step === 1 ? "space-y-4" : "hidden"}>
        <div className="surface flex items-center justify-between gap-3 p-4">
          <div>
            <span className="label">Cliente selecionado</span>
            <p className="font-semibold text-stone-950">{selectedCustomer?.name}</p>
          </div>
          <button className="btn-secondary" type="button" onClick={() => setStep(0)}>
            Trocar cliente
          </button>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          {machines.map((machine) => (
            <button
              key={machine.id}
              className={[
                "rounded-md border bg-white p-4 text-left shadow-sm transition hover:border-field-700 hover:bg-field-50",
                selectedMachine?.id === machine.id ? "border-field-700 ring-2 ring-field-100" : "border-stone-200",
              ].join(" ")}
              type="button"
              onClick={() => {
                setSelectedMachine(machine);
                setStep(2);
              }}
            >
              <p className="font-semibold text-stone-950">{machine.type}</p>
              <p className="mt-1 text-sm text-stone-700">{[machine.brand, machine.model].filter(Boolean).join(" / ") || "-"}</p>
              <p className="text-xs text-stone-500">Série: {machine.serial_number || "-"}</p>
            </button>
          ))}
        </div>

        {!loadingMachines && machines.length === 0 ? (
          <EmptyState
            icon={Tractor}
            title="Cliente sem máquinas cadastradas"
            description="Cadastre a máquina aqui mesmo para continuar a entrada."
            action={
              <button className="btn-primary" type="button" onClick={() => setMachineModalOpen(true)}>
                <Plus size={17} aria-hidden="true" />
                Nova máquina
              </button>
            }
          />
        ) : (
          <button className="btn-secondary" type="button" onClick={() => setMachineModalOpen(true)}>
            <Plus size={17} aria-hidden="true" />
            Nova máquina
          </button>
        )}
      </section>

      <section className={step === 2 ? "space-y-4" : "hidden"}>
        <div className="surface grid gap-4 p-4 md:grid-cols-2">
          <div>
            <span className="label">Cliente</span>
            <p className="font-semibold text-stone-950">{selectedCustomer?.name}</p>
          </div>
          <div>
            <span className="label">Máquina</span>
            <p className="font-semibold text-stone-950">{selectedMachine ? machineLabel(selectedMachine) : "-"}</p>
          </div>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Problema relatado pelo cliente</span>
            <textarea
              className="form-field min-h-28"
              value={reportedProblem}
              onChange={(event) => setReportedProblem(event.target.value)}
              placeholder="Descreva exatamente o que o cliente informou."
            />
          </label>
          <div className="md:col-span-2">
            <span className="label">Acessórios entregues</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {accessoryOptions.map((option) => (
                <button
                  key={option}
                  className={[
                    "rounded-md border px-3 py-2 text-sm font-semibold transition",
                    selectedAccessories.includes(option)
                      ? "border-field-700 bg-field-50 text-field-900"
                      : "border-stone-300 bg-white text-stone-700 hover:border-field-700",
                  ].join(" ")}
                  type="button"
                  onClick={() => toggleAccessory(option)}
                >
                  {option}
                </button>
              ))}
            </div>
            <input
              className="form-field mt-2"
              value={accessoryNotes}
              onChange={(event) => setAccessoryNotes(event.target.value)}
              placeholder="Outros acessórios ou detalhes"
            />
          </div>
          <label className="block space-y-1">
            <span className="label">Condição visual</span>
            <textarea
              className="form-field min-h-24"
              value={visualCondition}
              onChange={(event) => setVisualCondition(event.target.value)}
              placeholder="Ex.: carenagem riscada, sem lâmina, tanque vazio."
            />
          </label>
          <label className="block space-y-1">
            <span className="label">Observações internas</span>
            <textarea className="form-field min-h-24" value={notes} onChange={(event) => setNotes(event.target.value)} />
          </label>
        </div>
        <div className="flex justify-between gap-2">
          <button className="btn-secondary" type="button" onClick={() => setStep(1)}>
            Voltar
          </button>
          <button className="btn-primary" type="button" onClick={() => setStep(3)}>
            Continuar
          </button>
        </div>
      </section>

      <section className={step === 3 ? "space-y-4" : "hidden"}>
        <div className="grid gap-4 lg:grid-cols-2">
          {[
            {
              value: "SERVICO_DIRETO" as AttendanceType,
              icon: BadgeCheck,
              title: "Executar serviço",
              description: "Cliente já autorizou a execução do serviço.",
            },
            {
              value: "ORCAMENTO" as AttendanceType,
              icon: FileText,
              title: "Fazer orçamento",
              description: "A máquina será analisada antes da autorização.",
            },
          ].map((option) => {
            const Icon = option.icon;
            const selected = attendanceType === option.value;
            return (
              <button
                key={option.value}
                className={[
                  "rounded-md border bg-white p-5 text-left shadow-sm transition hover:border-field-700",
                  selected ? "border-field-700 bg-field-50 ring-2 ring-field-100" : "border-stone-200",
                ].join(" ")}
                type="button"
                onClick={() => setAttendanceType(option.value)}
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-md bg-field-700 text-white">
                  <Icon size={20} aria-hidden="true" />
                </span>
                <h2 className="mt-4 text-lg font-bold text-stone-950">{option.title}</h2>
                <p className="mt-1 text-sm text-stone-600">{option.description}</p>
              </button>
            );
          })}
        </div>

        <div className="surface p-4">
          <h2 className="text-base font-semibold text-stone-950">Resumo da entrada</h2>
          <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
            <div>
              <dt className="label">Cliente</dt>
              <dd className="font-medium">{selectedCustomer?.name}</dd>
            </div>
            <div>
              <dt className="label">Máquina</dt>
              <dd className="font-medium">{selectedMachine ? machineLabel(selectedMachine) : "-"}</dd>
            </div>
            <div>
              <dt className="label">Atendimento</dt>
              <dd className="font-medium">{formatAttendanceType(attendanceType)}</dd>
            </div>
            <div>
              <dt className="label">Acessórios</dt>
              <dd className="font-medium">{accessories || "-"}</dd>
            </div>
          </dl>
        </div>

        <div className="flex justify-between gap-2">
          <button className="btn-secondary" type="button" onClick={() => setStep(2)}>
            Voltar
          </button>
          <button className="btn-primary" type="button" disabled={isSubmitting} onClick={submitEntry}>
            <CheckCircle2 size={17} aria-hidden="true" />
            {isSubmitting ? "Criando..." : "Confirmar entrada"}
          </button>
        </div>
      </section>

      <Modal title="Novo cliente" open={customerModalOpen} onClose={() => setCustomerModalOpen(false)} size="xl">
        <form className="grid gap-4 md:grid-cols-2" onSubmit={createCustomer}>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Nome / Razão social</span>
            <input className="form-field" value={customerDraft.name} onChange={(event) => setCustomerDraft({ ...customerDraft, name: event.target.value })} autoFocus />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Nome fantasia</span>
            <input className="form-field" value={customerDraft.trade_name} onChange={(event) => setCustomerDraft({ ...customerDraft, trade_name: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">CPF/CNPJ</span>
            <input className="form-field" value={customerDraft.document} onChange={(event) => setCustomerDraft({ ...customerDraft, document: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Telefone</span>
            <input className="form-field" value={customerDraft.phone} onChange={(event) => setCustomerDraft({ ...customerDraft, phone: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">WhatsApp</span>
            <input className="form-field" value={customerDraft.whatsapp} onChange={(event) => setCustomerDraft({ ...customerDraft, whatsapp: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Email</span>
            <input className="form-field" type="email" value={customerDraft.email} onChange={(event) => setCustomerDraft({ ...customerDraft, email: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">CEP</span>
            <input className="form-field" value={customerDraft.zip_code} onChange={(event) => setCustomerDraft({ ...customerDraft, zip_code: event.target.value })} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Endereco</span>
            <input className="form-field" value={customerDraft.address} onChange={(event) => setCustomerDraft({ ...customerDraft, address: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Numero</span>
            <input className="form-field" value={customerDraft.number} onChange={(event) => setCustomerDraft({ ...customerDraft, number: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Bairro</span>
            <input className="form-field" value={customerDraft.district} onChange={(event) => setCustomerDraft({ ...customerDraft, district: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Cidade</span>
            <input className="form-field" value={customerDraft.city} onChange={(event) => setCustomerDraft({ ...customerDraft, city: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">UF</span>
            <input className="form-field uppercase" maxLength={2} value={customerDraft.state} onChange={(event) => setCustomerDraft({ ...customerDraft, state: event.target.value.toUpperCase() })} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Observacoes</span>
            <textarea className="form-field min-h-20" value={customerDraft.notes} onChange={(event) => setCustomerDraft({ ...customerDraft, notes: event.target.value })} />
          </label>
          <div className="flex justify-end gap-2 md:col-span-2">
            <button className="btn-secondary" type="button" onClick={() => setCustomerModalOpen(false)}>
              Cancelar
            </button>
            <button className="btn-primary" type="submit">
              Salvar cliente
            </button>
          </div>
        </form>
      </Modal>

      <Modal title="Nova máquina" open={machineModalOpen} onClose={() => setMachineModalOpen(false)}>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={createMachine}>
          <label className="block space-y-1">
            <span className="label">Tipo</span>
            <input className="form-field" value={machineDraft.type} onChange={(event) => setMachineDraft({ ...machineDraft, type: event.target.value })} autoFocus />
          </label>
          <label className="block space-y-1">
            <span className="label">Marca</span>
            <input className="form-field" value={machineDraft.brand} onChange={(event) => setMachineDraft({ ...machineDraft, brand: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Modelo</span>
            <input className="form-field" value={machineDraft.model} onChange={(event) => setMachineDraft({ ...machineDraft, model: event.target.value })} />
          </label>
          <label className="block space-y-1">
            <span className="label">Número de série</span>
            <input className="form-field" value={machineDraft.serial_number} onChange={(event) => setMachineDraft({ ...machineDraft, serial_number: event.target.value })} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Identificação física</span>
            <input className="form-field" value={machineDraft.identification} onChange={(event) => setMachineDraft({ ...machineDraft, identification: event.target.value })} />
          </label>
          <div className="flex justify-end gap-2 md:col-span-2">
            <button className="btn-secondary" type="button" onClick={() => setMachineModalOpen(false)}>
              Cancelar
            </button>
            <button className="btn-primary" type="submit">
              Salvar máquina
            </button>
          </div>
        </form>
      </Modal>

      <Modal title="Entrada criada" open={Boolean(result)} onClose={() => setResult(null)}>
        {result ? (
          <div className="space-y-5">
            <div className="rounded-md border border-emerald-200 bg-emerald-50 p-4 text-emerald-950">
              <p className="text-lg font-bold">Entrada {result.entry.number} criada com sucesso.</p>
              <p className="text-sm">OS {result.work_order_number} gerada para {formatAttendanceType(result.entry.attendance_type).toLowerCase()}.</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <button className="btn-secondary" type="button" onClick={() => printDocument("receipt")}>
                <Printer size={17} aria-hidden="true" />
                Imprimir via do cliente
              </button>
              <button className="btn-secondary" type="button" onClick={() => printDocument("tag")}>
                <Printer size={17} aria-hidden="true" />
                Imprimir identificação
              </button>
              <Link className="btn-primary" to={`/ordens-servico/${result.work_order_id}`}>
                <ClipboardList size={17} aria-hidden="true" />
                Abrir OS
              </Link>
              <button className="btn-secondary" type="button" onClick={resetFlow}>
                <Plus size={17} aria-hidden="true" />
                Nova entrada
              </button>
            </div>
          </div>
        ) : null}
      </Modal>

      {printMode && result ? (
        <div className="fixed inset-0 z-[60] overflow-auto bg-white p-5">
          <div className="no-print mb-4 flex justify-end gap-2">
            <button className="btn-secondary" type="button" onClick={() => window.print()}>
              <Printer size={17} aria-hidden="true" />
              Imprimir novamente
            </button>
            <button className="btn-primary" type="button" onClick={() => setPrintMode(null)}>
              Fechar
            </button>
          </div>
          {printMode === "receipt" ? (
            <CustomerEntryReceipt result={result} customer={selectedCustomer ?? undefined} machine={selectedMachine ?? undefined} />
          ) : (
            <MachineTag result={result} customer={selectedCustomer ?? undefined} machine={selectedMachine ?? undefined} />
          )}
        </div>
      ) : null}
    </div>
  );
}
