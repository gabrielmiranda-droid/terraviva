import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type EmptyStateProps = {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center rounded-md border border-dashed border-stone-300 bg-white px-6 py-10 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-md bg-stone-100 text-stone-600">
        <Icon size={21} aria-hidden="true" />
      </span>
      <h2 className="mt-3 text-base font-semibold text-stone-950">{title}</h2>
      <p className="mt-1 max-w-md text-sm text-stone-600">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
