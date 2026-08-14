import { Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AppLayout } from "../layouts/AppLayout";
import { useAuth } from "../hooks/useAuth";
import { CustomerDetailPage } from "../pages/CustomerDetailPage";
import { CustomersPage } from "../pages/CustomersPage";
import { BudgetsPage } from "../pages/BudgetsPage";
import { CounterSalePage } from "../pages/CounterSalePage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { MachineEntryPage } from "../pages/MachineEntryPage";
import { MachinesInShopPage } from "../pages/MachinesInShopPage";
import { MachinesPage } from "../pages/MachinesPage";
import { NewCustomerPage } from "../pages/NewCustomerPage";
import { NewMachinePage } from "../pages/NewMachinePage";
import { ProductsPage } from "../pages/ProductsPage";
import { StockPage } from "../pages/StockPage";
import { WorkOrderDetailPage } from "../pages/WorkOrderDetailPage";
import { WorkOrdersPage } from "../pages/WorkOrdersPage";

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="p-6 text-sm text-stone-600">Carregando...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <AppLayout />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route index element={<DashboardPage />} />
        <Route path="/clientes" element={<CustomersPage />} />
        <Route path="/clientes/novo" element={<NewCustomerPage />} />
        <Route path="/clientes/:customerId" element={<CustomerDetailPage />} />
        <Route path="/maquinas" element={<MachinesPage />} />
        <Route path="/maquinas/nova" element={<NewMachinePage />} />
        <Route path="/produtos" element={<ProductsPage />} />
        <Route path="/estoque" element={<StockPage />} />
        <Route path="/venda-balcao" element={<CounterSalePage />} />
        <Route path="/entrada" element={<MachineEntryPage />} />
        <Route path="/oficina" element={<MachinesInShopPage />} />
        <Route path="/orcamentos" element={<BudgetsPage />} />
        <Route path="/ordens-servico" element={<WorkOrdersPage />} />
        <Route path="/ordens-servico/:workOrderId" element={<WorkOrderDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
