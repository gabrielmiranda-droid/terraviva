from decimal import Decimal

from pydantic import BaseModel


class ErpProductRead(BaseModel):
    produto_id: int
    sku: str | None
    descricao: str
    marca: str | None
    unidade: str
    preco_venda: Decimal | None
    estoque: Decimal
    local_estoque: str | None
    alocacao: str | None
    status: str
    origem_linha_excel: int | None


class ErpProductSummary(BaseModel):
    total_produtos: int
    produtos_ativos: int
    produtos_com_estoque_negativo: int
    valor_total_estoque_venda: Decimal
