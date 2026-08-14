import { zodResolver } from "@hookform/resolvers/zod";
import { Save } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { Customer } from "../types/domain";
import { getErrorMessage } from "../utils/errors";

const schema = z.object({
  name: z.string().min(2, "Informe o nome."),
  trade_name: z.string().optional(),
  document: z.string().optional(),
  state_registration: z.string().optional(),
  phone: z.string().optional(),
  whatsapp: z.string().optional(),
  email: z.string().email("Email invalido.").optional().or(z.literal("")),
  zip_code: z.string().optional(),
  address: z.string().optional(),
  number: z.string().optional(),
  complement: z.string().optional(),
  district: z.string().optional(),
  city: z.string().optional(),
  state: z.string().max(2, "Use a UF.").optional(),
  notes: z.string().optional(),
});

type CustomerForm = z.infer<typeof schema>;

export function NewCustomerPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CustomerForm>({ resolver: zodResolver(schema) });

  async function onSubmit(values: CustomerForm) {
    setError(null);
    try {
      const payload = Object.fromEntries(
        Object.entries(values).map(([key, value]) => [key, value === "" ? null : value]),
      );
      const { data } = await api.post<Customer>("/customers", payload);
      navigate(`/clientes/${data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Novo Cliente" actions={<Link className="btn-secondary" to="/clientes">Voltar</Link>} />

      <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
        <section className="grid gap-4 rounded-md border border-stone-200 bg-white p-4 shadow-sm md:grid-cols-2">
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Nome / Razao social</span>
            <input className="form-field" {...register("name")} autoFocus />
            {errors.name ? <span className="text-xs text-red-700">{errors.name.message}</span> : null}
          </label>
          <label className="block space-y-1">
            <span className="label">Nome fantasia</span>
            <input className="form-field" {...register("trade_name")} />
          </label>
          <label className="block space-y-1">
            <span className="label">CPF/CNPJ</span>
            <input className="form-field" {...register("document")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Inscricao estadual</span>
            <input className="form-field" {...register("state_registration")} />
          </label>
          <label className="block space-y-1">
            <span className="label">Email</span>
            <input className="form-field" type="email" {...register("email")} />
            {errors.email ? <span className="text-xs text-red-700">{errors.email.message}</span> : null}
          </label>
          <label className="block space-y-1">
            <span className="label">Telefone</span>
            <input className="form-field" {...register("phone")} />
          </label>
          <label className="block space-y-1">
            <span className="label">WhatsApp</span>
            <input className="form-field" {...register("whatsapp")} />
          </label>
        </section>

        <section className="grid gap-4 rounded-md border border-stone-200 bg-white p-4 shadow-sm md:grid-cols-6">
          <label className="block space-y-1 md:col-span-1">
            <span className="label">CEP</span>
            <input className="form-field" {...register("zip_code")} />
          </label>
          <label className="block space-y-1 md:col-span-3">
            <span className="label">Endereco</span>
            <input className="form-field" {...register("address")} />
          </label>
          <label className="block space-y-1 md:col-span-1">
            <span className="label">Numero</span>
            <input className="form-field" {...register("number")} />
          </label>
          <label className="block space-y-1 md:col-span-1">
            <span className="label">UF</span>
            <input className="form-field uppercase" maxLength={2} {...register("state")} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Complemento</span>
            <input className="form-field" {...register("complement")} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Bairro</span>
            <input className="form-field" {...register("district")} />
          </label>
          <label className="block space-y-1 md:col-span-2">
            <span className="label">Cidade</span>
            <input className="form-field" {...register("city")} />
          </label>
          <label className="block space-y-1 md:col-span-6">
            <span className="label">Observacoes</span>
            <textarea className="form-field min-h-24" {...register("notes")} />
          </label>
        </section>

        {error ? <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}

        <div className="flex justify-end gap-2">
          <Link className="btn-secondary" to="/clientes">Cancelar</Link>
          <button className="btn-primary" type="submit" disabled={isSubmitting}>
            <Save size={17} aria-hidden="true" />
            Salvar
          </button>
        </div>
      </form>
    </div>
  );
}
