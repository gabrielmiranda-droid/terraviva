import {
  BadgeCheck,
  Ban,
  CheckCircle2,
  CircleDot,
  Clock3,
  HelpCircle,
  PackageCheck,
  PauseCircle,
  Stethoscope,
  Truck,
  Wrench,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type StatusMeta = {
  label: string;
  description: string;
  className: string;
  icon: LucideIcon;
};

export const STATUS_META: Record<string, StatusMeta> = {
  RECEBIDA: {
    label: "Recebida",
    description: "Entrada registrada e aguardando triagem.",
    className: "bg-sky-50 text-sky-800 ring-sky-200",
    icon: CircleDot,
  },
  AGUARDANDO_DIAGNOSTICO: {
    label: "Aguardando diagnóstico",
    description: "A máquina precisa ser analisada pelo técnico.",
    className: "bg-blue-50 text-blue-800 ring-blue-200",
    icon: Stethoscope,
  },
  EM_DIAGNOSTICO: {
    label: "Em diagnóstico",
    description: "Técnico avaliando o problema informado.",
    className: "bg-blue-50 text-blue-800 ring-blue-200",
    icon: Stethoscope,
  },
  AGUARDANDO_ORCAMENTO: {
    label: "Aguardando orçamento",
    description: "Diagnóstico feito e orçamento pendente.",
    className: "bg-amber-50 text-amber-800 ring-amber-200",
    icon: Clock3,
  },
  AGUARDANDO_APROVACAO: {
    label: "Aguardando aprovação",
    description: "Orçamento enviado e aguardando resposta do cliente.",
    className: "bg-amber-50 text-amber-800 ring-amber-200",
    icon: Clock3,
  },
  APROVADA: {
    label: "Autorizada",
    description: "Cliente autorizou a execução.",
    className: "bg-emerald-50 text-emerald-800 ring-emerald-200",
    icon: BadgeCheck,
  },
  RECUSADA: {
    label: "Recusada",
    description: "Cliente recusou o orçamento.",
    className: "bg-red-50 text-red-800 ring-red-200",
    icon: Ban,
  },
  AGUARDANDO_PECA: {
    label: "Aguardando peça",
    description: "Serviço parado aguardando peça.",
    className: "bg-orange-50 text-orange-800 ring-orange-200",
    icon: PauseCircle,
  },
  EM_MANUTENCAO: {
    label: "Em manutenção",
    description: "Serviço em execução na oficina.",
    className: "bg-lime-50 text-lime-800 ring-lime-200",
    icon: Wrench,
  },
  FINALIZADA: {
    label: "Finalizada",
    description: "Serviço concluído internamente.",
    className: "bg-teal-50 text-teal-800 ring-teal-200",
    icon: CheckCircle2,
  },
  PRONTA_PARA_ENTREGA: {
    label: "Pronta para retirada",
    description: "Máquina pronta para o cliente retirar.",
    className: "bg-emerald-50 text-emerald-800 ring-emerald-200",
    icon: PackageCheck,
  },
  ENTREGUE: {
    label: "Entregue",
    description: "Máquina entregue e fora da oficina.",
    className: "bg-stone-100 text-stone-800 ring-stone-200",
    icon: Truck,
  },
  CANCELADA: {
    label: "Cancelada",
    description: "Atendimento cancelado.",
    className: "bg-red-50 text-red-800 ring-red-200",
    icon: Ban,
  },
};

export function getStatusMeta(status: string): StatusMeta {
  return (
    STATUS_META[status] ?? {
      label: status.replace(/_/g, " ").toLowerCase(),
      description: "Status operacional.",
      className: "bg-stone-100 text-stone-800 ring-stone-200",
      icon: HelpCircle,
    }
  );
}

export function formatAttendanceType(value: string) {
  return value === "ORCAMENTO" ? "Fazer orçamento" : "Executar serviço";
}
