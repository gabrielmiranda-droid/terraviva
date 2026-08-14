import {
  BarChart3,
  Boxes,
  ClipboardList,
  FileBarChart,
  FileText,
  LayoutDashboard,
  LogOut,
  PackageSearch,
  PanelLeftClose,
  Plus,
  Receipt,
  Search,
  Settings,
  ShoppingCart,
  Tractor,
  UserCog,
  Users,
  Warehouse,
  Wrench,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

type NavItem = {
  to?: string;
  label: string;
  icon: LucideIcon;
  highlight?: boolean;
  disabled?: boolean;
};

const sections: Array<{ title: string; items: NavItem[] }> = [
  {
    title: "Visão geral",
    items: [{ to: "/", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    title: "Oficina",
    items: [
      { to: "/entrada", label: "Nova Entrada", icon: Plus, highlight: true },
      { to: "/oficina", label: "Máquinas na Oficina", icon: Tractor },
      { to: "/ordens-servico", label: "Ordens de Serviço", icon: ClipboardList },
      { to: "/orcamentos", label: "Orçamentos", icon: FileText },
    ],
  },
  {
    title: "Comercial",
    items: [
      { to: "/venda-balcao", label: "Venda Balcão", icon: ShoppingCart },
      { to: "/produtos", label: "Produtos", icon: PackageSearch },
      { to: "/estoque", label: "Estoque", icon: Warehouse },
    ],
  },
  {
    title: "Cadastros",
    items: [
      { to: "/clientes", label: "Clientes", icon: Users },
      { to: "/maquinas", label: "Máquinas", icon: Boxes },
      { label: "Fornecedores", icon: Receipt, disabled: true },
    ],
  },
  {
    title: "Gestão",
    items: [
      { label: "Financeiro", icon: BarChart3, disabled: true },
      { label: "Relatórios", icon: FileBarChart, disabled: true },
      { label: "Usuários", icon: UserCog, disabled: true },
      { label: "Configurações", icon: Settings, disabled: true },
    ],
  },
];

function SidebarItem({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  const Icon = item.icon;
  if (!item.to || item.disabled) {
    return (
      <span
        className={[
          "flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-stone-400",
          collapsed ? "justify-center" : "",
        ].join(" ")}
        title={item.label}
      >
        <Icon size={17} aria-hidden="true" />
        {collapsed ? null : item.label}
      </span>
    );
  }
  return (
    <NavLink
      to={item.to}
      className={({ isActive }) =>
        [
          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold transition",
          collapsed ? "justify-center" : "",
          item.highlight && !isActive ? "bg-field-700 text-white shadow-sm hover:bg-field-800" : "",
          isActive && item.highlight ? "bg-field-800 text-white shadow-sm" : "",
          isActive && !item.highlight ? "bg-field-50 text-field-900" : "",
          !isActive && !item.highlight ? "text-stone-700 hover:bg-stone-100 hover:text-stone-950" : "",
        ].join(" ")
      }
      title={item.label}
    >
      <Icon size={17} aria-hidden="true" />
      {collapsed ? null : item.label}
    </NavLink>
  );
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const mobileLinks = sections.flatMap((section) => section.items.filter((item) => item.to));

  return (
    <div className="min-h-screen bg-[#f3f5f1] text-stone-900">
      <aside
        className={[
          "fixed inset-y-0 left-0 hidden border-r border-stone-200 bg-white px-4 py-5 transition-all lg:block",
          collapsed ? "w-20" : "w-72",
        ].join(" ")}
      >
        <div className={["flex items-center gap-3 border-b border-stone-200 pb-5", collapsed ? "justify-center" : ""].join(" ")}>
          <span className="flex h-11 w-11 items-center justify-center rounded-md bg-field-800 text-white">
            <Wrench size={21} aria-hidden="true" />
          </span>
          <div className={collapsed ? "hidden" : ""}>
            <p className="text-sm font-bold text-stone-950">ERP Oficina Agrícola</p>
            <p className="text-xs text-stone-500">Operação de oficina e estoque</p>
          </div>
        </div>

        <nav className="mt-5 space-y-5">
          {sections.map((section) => (
            <section key={section.title}>
              <h2 className={["mb-2 px-3 text-[11px] font-bold uppercase tracking-normal text-stone-400", collapsed ? "sr-only" : ""].join(" ")}>
                {section.title}
              </h2>
              <div className="space-y-1">
                {section.items.map((item) => (
                  <SidebarItem key={item.label} item={item} collapsed={collapsed} />
                ))}
              </div>
            </section>
          ))}
        </nav>
      </aside>

      <div className={collapsed ? "lg:pl-20" : "lg:pl-72"}>
        <header className="sticky top-0 z-20 border-b border-stone-200 bg-white/95 px-4 py-3 backdrop-blur">
          <div className="mx-auto flex max-w-7xl items-center gap-3">
            <nav className="flex gap-1 overflow-x-auto lg:hidden">
              {mobileLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <NavLink
                    key={link.to}
                    to={link.to ?? "/"}
                    className={({ isActive }) =>
                      [
                        "inline-flex min-h-10 min-w-10 items-center justify-center rounded-md px-3 text-sm font-medium",
                        isActive ? "bg-field-50 text-field-800" : "text-stone-700",
                      ].join(" ")
                    }
                    title={link.label}
                  >
                    <Icon size={18} aria-hidden="true" />
                  </NavLink>
                );
              })}
            </nav>

            <button
              className="icon-button hidden lg:inline-flex"
              type="button"
              onClick={() => setCollapsed((value) => !value)}
              title={collapsed ? "Expandir menu" : "Recolher menu"}
            >
              <PanelLeftClose size={17} aria-hidden="true" />
            </button>

            <label className="relative hidden min-w-0 flex-1 md:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={17} />
              <input
                className="form-field bg-stone-50 pl-9"
                placeholder="Busca global: cliente, máquina, OS, produto..."
                readOnly
              />
            </label>

            <NavLink className="btn-primary ml-auto" to="/entrada">
              <Plus size={17} aria-hidden="true" />
              <span className="hidden sm:inline">Nova Entrada</span>
            </NavLink>

            <div className="hidden text-right sm:block">
              <p className="text-sm font-semibold text-stone-950">{user?.full_name}</p>
              <p className="text-xs text-stone-500">{user?.role?.name}</p>
            </div>
            <button className="btn-secondary px-3" type="button" onClick={logout} title="Sair">
              <LogOut size={17} aria-hidden="true" />
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
