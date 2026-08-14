import { getStatusMeta } from "../utils/status";

export function StatusBadge({ status }: { status: string }) {
  const meta = getStatusMeta(status);
  const Icon = meta.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-semibold ring-1 ${meta.className}`}>
      <Icon size={13} aria-hidden="true" />
      {meta.label}
    </span>
  );
}
