import { X } from "lucide-react";
import type { ReactNode } from "react";

type ModalProps = {
  title: string;
  open: boolean;
  children: ReactNode;
  onClose: () => void;
  size?: "md" | "lg" | "xl";
};

const sizes = {
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-5xl",
};

export function Modal({ title, open, children, onClose, size = "lg" }: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/45 px-4 py-6">
      <div className={`max-h-[92vh] w-full overflow-hidden rounded-md bg-white shadow-xl ${sizes[size]}`}>
        <div className="flex items-center justify-between border-b border-stone-200 px-5 py-4">
          <h2 className="text-base font-semibold text-stone-950">{title}</h2>
          <button className="icon-button" type="button" onClick={onClose} title="Fechar">
            <X size={18} aria-hidden="true" />
          </button>
        </div>
        <div className="max-h-[calc(92vh-65px)] overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  );
}
