import { Plus } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { Machine } from "../types/domain";

async function fetchMachines(search: string) {
  const { data } = await api.get<Machine[]>("/machines", { params: { search: search || undefined, limit: 200 } });
  return data;
}

export function MachinesPage() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data: machines = [], isLoading } = useQuery({
    queryKey: ["machines", debouncedSearch],
    queryFn: () => fetchMachines(debouncedSearch),
  });
  return (
    <div className="space-y-5">
      <PageHeader
        title="Maquinas"
        actions={
          <Link className="btn-primary" to="/maquinas/nova">
            <Plus size={17} aria-hidden="true" />
            Nova maquina
          </Link>
        }
      />

      <section className="surface p-3">
        <SearchField
          value={search}
          onChange={setSearch}
          placeholder="Buscar por cliente, tipo, marca, modelo, serie ou identificacao"
          ariaLabel="Buscar maquinas"
        />
      </section>

      <div className="overflow-hidden rounded-md border border-stone-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-stone-200 text-sm">
            <thead className="bg-stone-50 text-left text-xs font-semibold uppercase tracking-normal text-stone-600">
              <tr>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Cliente</th>
                <th className="px-4 py-3">Marca / modelo</th>
                <th className="px-4 py-3">Serie</th>
                <th className="px-4 py-3">Identificacao</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {machines.map((machine) => (
                <tr key={machine.id} className="hover:bg-stone-50">
                  <td className="px-4 py-3 font-medium text-stone-950">{machine.type}</td>
                  <td className="px-4 py-3 text-stone-700">{machine.customer_name || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">
                    {[machine.brand, machine.model].filter(Boolean).join(" / ") || "-"}
                  </td>
                  <td className="px-4 py-3 text-stone-700">{machine.serial_number || "-"}</td>
                  <td className="px-4 py-3 text-stone-700">{machine.identification || "-"}</td>
                </tr>
              ))}
              {!isLoading && machines.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-stone-500" colSpan={5}>
                    Nenhuma maquina encontrada.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
