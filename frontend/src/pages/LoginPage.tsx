import { zodResolver } from "@hookform/resolvers/zod";
import { LogIn, Wrench } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { useAuth } from "../hooks/useAuth";
import { getErrorMessage } from "../utils/errors";

const schema = z.object({
  email: z.string().email("Informe um email valido."),
  password: z.string().min(1, "Informe a senha."),
});

type LoginForm = z.infer<typeof schema>;

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const from = (location.state as { from?: Location } | null)?.from?.pathname ?? "/";
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(schema),
    defaultValues: { email: "admin@geleia.local", password: "admin123" },
  });

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(values: LoginForm) {
    setError(null);
    try {
      await login(values.email, values.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-stone-100 px-4 py-10">
      <section className="w-full max-w-md rounded-md border border-stone-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-md bg-field-800 text-white">
            <Wrench size={22} aria-hidden="true" />
          </span>
          <div>
            <h1 className="text-xl font-semibold tracking-normal text-stone-950">ERP Oficina Agricola</h1>
            <p className="text-sm text-stone-500">Acesso operacional</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <label className="block space-y-1">
            <span className="label">Email</span>
            <input className="form-field" type="email" {...register("email")} />
            {errors.email ? <span className="text-xs text-red-700">{errors.email.message}</span> : null}
          </label>

          <label className="block space-y-1">
            <span className="label">Senha</span>
            <input className="form-field" type="password" {...register("password")} />
            {errors.password ? (
              <span className="text-xs text-red-700">{errors.password.message}</span>
            ) : null}
          </label>

          {error ? (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
              {error}
            </div>
          ) : null}

          <button className="btn-primary w-full" type="submit" disabled={isSubmitting}>
            <LogIn size={17} aria-hidden="true" />
            Entrar
          </button>
        </form>
      </section>
    </main>
  );
}
