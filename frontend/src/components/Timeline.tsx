import { getStatusMeta } from "../utils/status";

type TimelineItem = {
  status: string;
  date?: string | null;
  reason?: string | null;
};

export function Timeline({ items }: { items: TimelineItem[] }) {
  return (
    <ol className="space-y-3">
      {items.map((item, index) => {
        const meta = getStatusMeta(item.status);
        const Icon = meta.icon;
        return (
          <li key={`${item.status}-${item.date ?? index}`} className="flex gap-3">
            <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md ring-1 ${meta.className}`}>
              <Icon size={16} aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-stone-950">{meta.label}</p>
              {item.date ? (
                <p className="text-xs text-stone-500">
                  {new Date(item.date).toLocaleString("pt-BR")}
                </p>
              ) : null}
              {item.reason ? <p className="mt-1 text-sm text-stone-600">{item.reason}</p> : null}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
