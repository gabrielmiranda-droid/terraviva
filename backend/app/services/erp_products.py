from decimal import Decimal

from sqlalchemy import String, func, or_, select
from sqlalchemy.orm import Session

from app.models.supabase_erp import (
    ErpEstoqueSaldo,
    ErpLocalEstoque,
    ErpMarca,
    ErpPrecoProduto,
    ErpProduto,
    ErpUnidadeMedida,
)
from app.schemas.erp_product import ErpProductRead, ErpProductSummary


def list_erp_products(
    db: Session,
    *,
    search: str | None,
    offset: int,
    limit: int,
) -> list[ErpProductRead]:
    price_subquery = (
        select(
            ErpPrecoProduto.produto_id,
            func.max(ErpPrecoProduto.preco_venda).label("preco_venda"),
        )
        .where(ErpPrecoProduto.tabela_preco == "PADRAO")
        .group_by(ErpPrecoProduto.produto_id)
        .subquery()
    )
    stock_subquery = (
        select(
            ErpEstoqueSaldo.produto_id,
            func.coalesce(func.sum(ErpEstoqueSaldo.quantidade), 0).label("estoque"),
            func.string_agg(func.distinct(ErpLocalEstoque.nome), ", ").label("local_estoque"),
            func.string_agg(
                func.distinct(func.nullif(func.trim(ErpEstoqueSaldo.alocacao), "")),
                ", ",
            ).label("alocacao"),
        )
        .outerjoin(ErpLocalEstoque, ErpLocalEstoque.local_estoque_id == ErpEstoqueSaldo.local_estoque_id)
        .group_by(ErpEstoqueSaldo.produto_id)
        .subquery()
    )

    stmt = (
        select(
            ErpProduto.produto_id,
            ErpProduto.sku,
            ErpProduto.descricao,
            ErpMarca.nome.label("marca"),
            ErpUnidadeMedida.codigo.label("unidade"),
            price_subquery.c.preco_venda,
            func.coalesce(stock_subquery.c.estoque, 0).label("estoque"),
            stock_subquery.c.local_estoque,
            stock_subquery.c.alocacao,
            ErpProduto.status,
            ErpProduto.origem_linha_excel,
        )
        .join(ErpUnidadeMedida, ErpUnidadeMedida.unidade_medida_id == ErpProduto.unidade_medida_id)
        .outerjoin(ErpMarca, ErpMarca.marca_id == ErpProduto.marca_id)
        .outerjoin(price_subquery, price_subquery.c.produto_id == ErpProduto.produto_id)
        .outerjoin(stock_subquery, stock_subquery.c.produto_id == ErpProduto.produto_id)
        .order_by(ErpProduto.descricao.asc())
        .offset(offset)
        .limit(limit)
    )
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                ErpProduto.produto_id.cast(String).ilike(like),
                ErpProduto.descricao.ilike(like),
                ErpProduto.sku.ilike(like),
                ErpMarca.nome.ilike(like),
            )
        )

    return [ErpProductRead.model_validate(row._asdict()) for row in db.execute(stmt).all()]


def get_erp_product_summary(db: Session) -> ErpProductSummary:
    price_subquery = (
        select(
            ErpPrecoProduto.produto_id,
            func.max(ErpPrecoProduto.preco_venda).label("preco_venda"),
        )
        .where(ErpPrecoProduto.tabela_preco == "PADRAO")
        .group_by(ErpPrecoProduto.produto_id)
        .subquery()
    )
    stock_subquery = (
        select(
            ErpEstoqueSaldo.produto_id,
            func.coalesce(func.sum(ErpEstoqueSaldo.quantidade), 0).label("estoque"),
        )
        .group_by(ErpEstoqueSaldo.produto_id)
        .subquery()
    )
    totals = db.execute(
        select(
            func.count(ErpProduto.produto_id).label("total_produtos"),
            func.count(ErpProduto.produto_id).filter(ErpProduto.status == "ATIVO").label("produtos_ativos"),
            func.count(ErpProduto.produto_id)
            .filter(func.coalesce(stock_subquery.c.estoque, 0) < 0)
            .label("produtos_com_estoque_negativo"),
            func.coalesce(
                func.sum(func.coalesce(stock_subquery.c.estoque, 0) * func.coalesce(price_subquery.c.preco_venda, 0)),
                0,
            ).label("valor_total_estoque_venda"),
        )
        .outerjoin(stock_subquery, stock_subquery.c.produto_id == ErpProduto.produto_id)
        .outerjoin(price_subquery, price_subquery.c.produto_id == ErpProduto.produto_id)
    ).one()
    return ErpProductSummary(
        total_produtos=totals.total_produtos or 0,
        produtos_ativos=totals.produtos_ativos or 0,
        produtos_com_estoque_negativo=totals.produtos_com_estoque_negativo or 0,
        valor_total_estoque_venda=totals.valor_total_estoque_venda or Decimal("0"),
    )
