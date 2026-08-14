export type Role = {
  id: string;
  name: string;
  description?: string | null;
};

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: Role | null;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Customer = {
  id: string;
  name: string;
  trade_name?: string | null;
  document?: string | null;
  state_registration?: string | null;
  phone?: string | null;
  whatsapp?: string | null;
  email?: string | null;
  zip_code?: string | null;
  address?: string | null;
  number?: string | null;
  complement?: string | null;
  district?: string | null;
  city?: string | null;
  state?: string | null;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type Machine = {
  id: string;
  customer_id: string;
  type: string;
  brand?: string | null;
  model?: string | null;
  serial_number?: string | null;
  year?: number | null;
  identification?: string | null;
  usage_hours?: string | null;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DashboardMetrics = {
  machines_in_shop: number;
  entries_today: number;
  open_work_orders: number;
  waiting_diagnosis: number;
  waiting_approval: number;
  in_maintenance: number;
  ready_for_pickup: number;
};

export type DatabaseStatus = {
  mode: string;
  is_supabase: boolean;
  message: string;
};

export type AttendanceType = "SERVICO_DIRETO" | "ORCAMENTO";

export type MachineEntryResult = {
  entry: {
    id: string;
    number: string;
    public_token: string;
    customer_id: string;
    machine_id: string;
    entry_date: string;
    reported_problem: string;
    attendance_type: AttendanceType;
    accessories?: string | null;
    visual_condition?: string | null;
    notes?: string | null;
    status: string;
    delivered_at?: string | null;
    delivered_by_user_id?: string | null;
    receiver_name?: string | null;
    delivery_notes?: string | null;
  };
  work_order_id: string;
  work_order_number: string;
};

export type WorkOrder = {
  id: string;
  number: string;
  entry_id: string;
  customer_id: string;
  machine_id: string;
  technician_id?: string | null;
  reported_problem: string;
  diagnosis?: string | null;
  internal_notes?: string | null;
  priority: string;
  status: string;
  opened_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  delivered_at?: string | null;
  parts_total: string;
  services_total: string;
  discount: string;
  total: string;
  created_at: string;
  updated_at: string;
};

export type WorkshopMachine = {
  entry_id: string;
  entry_number: string;
  entry_public_token: string;
  work_order_id: string;
  work_order_number: string;
  customer_id: string;
  customer_name: string;
  customer_phone?: string | null;
  machine_id: string;
  machine_type: string;
  machine_brand?: string | null;
  machine_model?: string | null;
  machine_serial_number?: string | null;
  entered_at: string;
  days_in_shop: number;
  attendance_type: AttendanceType;
  status: string;
  technician_id?: string | null;
  technician_name?: string | null;
  reported_problem: string;
};

export type WorkshopFlow = {
  columns: Array<{ key: string; label: string; count: number }>;
  attention: Array<{
    entry_id: string;
    entry_number: string;
    work_order_id: string;
    work_order_number: string;
    customer_name: string;
    machine_label: string;
    status: string;
    days_in_shop: number;
    reported_problem: string;
  }>;
};

export type WorkOrderDetail = {
  work_order: WorkOrder;
  entry: MachineEntryResult["entry"] & {
    notes?: string | null;
    accessories?: string | null;
    visual_condition?: string | null;
  };
  customer: Customer;
  machine: Machine;
  history: Array<{
    id: string;
    work_order_id: string;
    from_status?: string | null;
    to_status: string;
    changed_by_user_id?: string | null;
    changed_at: string;
    reason?: string | null;
  }>;
};

export type PrintJob = {
  id: string;
  document_type: string;
  reference_type: string;
  reference_id: string;
  status: string;
  printer_name?: string | null;
  printed_at?: string | null;
};

export type ErpProduct = {
  produto_id: number;
  sku?: string | null;
  descricao: string;
  marca?: string | null;
  unidade: string;
  preco_venda?: string | null;
  estoque: string;
  local_estoque?: string | null;
  alocacao?: string | null;
  status: string;
  origem_linha_excel?: number | null;
};

export type ErpProductSummary = {
  total_produtos: number;
  produtos_ativos: number;
  produtos_com_estoque_negativo: number;
  valor_total_estoque_venda: string;
};

export type FiscalInvoiceStatus = "NOT_REQUESTED" | "PENDING" | "ISSUED" | "CANCELLED" | "ERROR";

export type Sale = {
  id: string;
  number: string;
  customer_id?: string | null;
  seller_id?: string | null;
  status: string;
  sold_at?: string | null;
  items_total: string;
  discount: string;
  total: string;
  fiscal_invoice_requested: boolean;
  fiscal_invoice_status: FiscalInvoiceStatus;
  fiscal_document?: string | null;
  fiscal_name?: string | null;
  fiscal_state_registration?: string | null;
  fiscal_email?: string | null;
  created_at: string;
  updated_at: string;
};
