import { zodResolver } from "@hookform/resolvers/zod";
import { Save } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";

import { PageHeader } from "../components/PageHeader";
import { SearchField } from "../components/SearchField";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api } from "../services/api";
import type { Customer, Machine } from "../types/domain";
import { getErrorMessage } from "../utils/errors";

const schema = z.object({
  customer_id: z.string().min(1, "Selecione o cliente."),
  type: z.string().min(2, "Informe o tipo."),
  brand: z.string().optional(),
  model: z.string().optional(),
  serial_number: z.string().optional(),
  year: z.coerce.number().int().min(1900).max(2100).optional().or(z.literal("")),
  identification: z.string().optional(),
  usage_hours: z.coerce.number().nonnegative().optional().or(z.literal("")),
  notes: z.string().optional(),
});

type MachineForm = z.infer<typeof schema>;

async function fetchCustomers(search: string) {
  const { data } = await api.get<Customer[]>("/customers", { params: { search: search || undefined, limit: 200 } });
  return data;
}

async function fetchCustomer(customerId: string) {
  const { data } = await api.get<Customer>(`/customers/${customerId}`);
  return data;
}

export function NewMachinePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [customerSearch, setCustomerSearch] = useState("");
  const debouncedCustomerSearch = useDebouncedValue(customerSearch);
  const selectedCustomerId = params.get("customer_id") ?? "";
  const { data: customers = [] } = useQuery({
    queryKey: ["customers", debouncedCustomerSearch],
    queryFn: () => fetchCustomers(debouncedCustomerSearch),
  });
  const { data: selectedCustomer } = useQuery({
    queryKey: ["customer", selectedCustomerId],
    queryFn: () => fetchCustomer(selectedCustomerId),
    enabled: Boolean(selectedCustomerId),
  });
  const customerOptions = selectedCustomer && !customers.some((customer) => customer.id === selectedCustomer.id)
    ? [selectedCustomer, ...customers]
    : customers;
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<MachineForm>({
    resolver: zodResolver(schema),
    defaultValues: { customer_id: selectedCustomerId },
  });

  async function onSubmit(values: MachineForm) {
    setError(null);
    try {
      const payload = Object.fromEntries(
        Object.entries(values).map(([key, value]) => [key, value === "" ? null : value]),
      );
      await api.post<Machine>("/machines", payload);
      navigate(params.get("customer_id") ? `/clientes/${params.get("customer_id")}` : "/maquinas");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Nova Maquina" actions={<Link className="btn-secondary" to="/maquinas">Voltar</Link>} />

      <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
        <section className="grid gap-4 rounded-md border border-stone-200 bg-white p-4 shadow-sm md:grid-cols-2">
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Cliente</span>
            <SearchField
              value={customerSearch}
              onChange={setCustomerSearch}
              placeholder="Buscar cliente por nome, documento ou telefone"
              ariaLabel="Buscar cliente da maquina"
              className="mb-2"
            />
            <select className="form-field" {...register("customer_id")}>
              <option value="">Selecione</option>
              {customerOptions.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
            {errors.customer_id ? <span className="text-xs text-red-700">{errors.customer_id.message}</span> : null}
          </label>
          <label className="block space-y-1">
            <span className="label">Tipo</span>
            <input className="form-field" {...register("type")} autoFocus />
            {errors.type ? <span className="text-xs text-red-700">{errors.type.message}</span> : null}
          </label>
          <label className="block space-y-1">
            <span className="label">Marca</span>
            <input className="form-field" {...register("brand")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Modelo</span>
            <input className="form-field" {...register("model")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Numero de serie</span>
            <input className="form-field" {...register("serial_number")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Ano</span>
            <input className="form-field" type="number" {...register("year")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Identificacao</span>
            <input className="form-field" {...register("identification")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Horas de uso</span>
            <input className="form-field" type="number" step="0.1" {...register("usage_hours")} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Observacoes</span>
            <textarea className="form-field min-h-24" {...register("notes")} />
          </label>
        </section>

        {error ? <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}

        <div className="flex justify-end gap-2">
          <Link className="btn-secondary" to="/maquinas">Cancelar</Link>
          <button className="btn-primary" type="submit" disabled={isSubmitting}>
            <Save size={17} aria-hidden="true" />
            Salvar
          </button>
        </div>
      </form>
    </div>
  );
}
