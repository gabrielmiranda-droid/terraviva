import { QrCode } from "./QrCode";
import type { Customer, Machine, MachineEntryResult } from "../types/domain";
import { formatAttendanceType } from "../utils/status";

type EntryPrintData = {
  result: MachineEntryResult;
  customer?: Customer;
  machine?: Machine;
};

function machineLabel(machine?: Machine) {
  if (!machine) return "-";
  return [machine.type, machine.brand, machine.model].filter(Boolean).join(" / ");
}

function publicUrl(token: string) {
  return `${window.location.origin}/consulta/${token}`;
}

export function CustomerEntryReceipt({ result, customer, machine }: EntryPrintData) {
  const entry = result.entry;
  return (
    <article className="print-area mx-auto max-w-3xl bg-white p-8 text-stone-950">
      <header className="flex items-start justify-between border-b-2 border-stone-900 pb-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-normal text-field-800">ERP Oficina Agrícola</p>
          <h1 className="mt-1 text-2xl font-bold">Comprovante de Entrada</h1>
          <p className="mt-1 text-sm text-stone-600">Via do cliente</p>
        </div>
        <QrCode value={publicUrl(entry.public_token)} size={104} />
      </header>

      <section className="mt-5 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="label">Entrada</span>
          <p className="text-lg font-bold">{entry.number}</p>
        </div>
        <div>
          <span className="label">Ordem de serviço</span>
          <p className="text-lg font-bold">{result.work_order_number}</p>
        </div>
        <div>
          <span className="label">Data e hora</span>
          <p>{new Date(entry.entry_date).toLocaleString("pt-BR")}</p>
        </div>
        <div>
          <span className="label">Tipo de atendimento</span>
          <p>{formatAttendanceType(entry.attendance_type)}</p>
        </div>
      </section>

      <section className="mt-6 grid grid-cols-2 gap-4 border-y border-stone-200 py-4 text-sm">
        <div>
          <span className="label">Cliente</span>
          <p className="font-semibold">{customer?.name ?? "-"}</p>
          <p className="text-stone-600">{customer?.whatsapp || customer?.phone || "-"}</p>
        </div>
        <div>
          <span className="label">Máquina</span>
          <p className="font-semibold">{machineLabel(machine)}</p>
          <p className="text-stone-600">Série: {machine?.serial_number || "-"}</p>
        </div>
      </section>

      <section className="mt-6 space-y-4 text-sm">
        <div>
          <span className="label">Problema relatado</span>
          <p className="mt-1 whitespace-pre-wrap rounded-md border border-stone-200 p-3">{entry.reported_problem}</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="label">Acessórios entregues</span>
            <p className="mt-1 whitespace-pre-wrap rounded-md border border-stone-200 p-3">{entry.accessories || "-"}</p>
          </div>
          <div>
            <span className="label">Condição visual</span>
            <p className="mt-1 whitespace-pre-wrap rounded-md border border-stone-200 p-3">{entry.visual_condition || "-"}</p>
          </div>
        </div>
        <div>
          <span className="label">Observações</span>
          <p className="mt-1 whitespace-pre-wrap rounded-md border border-stone-200 p-3">{entry.notes || "-"}</p>
        </div>
      </section>

      <footer className="mt-10 grid grid-cols-2 gap-8 text-sm">
        <div className="border-t border-stone-400 pt-2 text-center">Assinatura do cliente</div>
        <div className="border-t border-stone-400 pt-2 text-center">Recebido pela oficina</div>
      </footer>
    </article>
  );
}

export function MachineTag({ result, customer, machine }: EntryPrintData) {
  const entry = result.entry;
  return (
    <article className="print-area mx-auto flex max-w-md flex-col gap-4 bg-white p-6 text-stone-950">
      <header className="border-b-2 border-stone-900 pb-3">
        <p className="text-sm font-bold uppercase tracking-normal text-field-800">ERP Oficina Agrícola</p>
        <h1 className="mt-2 text-4xl font-black tracking-normal">{entry.number}</h1>
        <p className="text-xl font-bold">{result.work_order_number}</p>
      </header>
      <section className="grid grid-cols-[1fr_auto] gap-4">
        <div className="space-y-3">
          <div>
            <span className="label">Cliente</span>
            <p className="text-lg font-bold">{customer?.name ?? "-"}</p>
          </div>
          <div>
            <span className="label">Máquina</span>
            <p className="text-lg font-bold">{machineLabel(machine)}</p>
            <p className="text-sm text-stone-600">Série: {machine?.serial_number || "-"}</p>
          </div>
          <div>
            <span className="label">Data</span>
            <p className="font-semibold">{new Date(entry.entry_date).toLocaleDateString("pt-BR")}</p>
          </div>
        </div>
        <QrCode value={publicUrl(entry.public_token)} size={128} />
      </section>
    </article>
  );
}
