import type { LucideIcon } from "lucide-react";

type MetricCardProps = {
  title: string;
  value: number;
  icon: LucideIcon;
};

export function MetricCard({ title, value, icon: Icon }: MetricCardProps) {
  return (
    <div className="rounded-md border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-stone-600">{title}</span>
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-field-50 text-field-800">
          <Icon size={18} aria-hidden="true" />
        </span>
      </div>
      <strong className="mt-3 block text-3xl font-semibold tracking-normal text-stone-950">
        {value}
      </strong>
    </div>
  );
}
