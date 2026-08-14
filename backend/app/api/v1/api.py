from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, dashboard, erp_products, imports, machine_entries, machines, sales, work_orders

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["autenticacao"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(customers.router, prefix="/customers", tags=["clientes"])
api_router.include_router(machines.router, prefix="/machines", tags=["maquinas"])
api_router.include_router(machine_entries.router, prefix="/machine-entries", tags=["entradas"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["ordens de servico"])
api_router.include_router(sales.router, prefix="/sales", tags=["vendas"])
api_router.include_router(imports.router, prefix="/imports", tags=["importacao"])
api_router.include_router(erp_products.router, prefix="/erp-products", tags=["produtos supabase"])
