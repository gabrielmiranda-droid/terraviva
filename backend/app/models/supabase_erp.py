from __future__ import annotations

from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SupabaseErpBase(DeclarativeBase):
    pass


class ErpMarca(SupabaseErpBase):
    __tablename__ = "marcas"
    __table_args__ = {"schema": "erp"}

    marca_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(120), nullable=False)


class ErpUnidadeMedida(SupabaseErpBase):
    __tablename__ = "unidades_medida"
    __table_args__ = {"schema": "erp"}

    unidade_medida_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(12), nullable=False)
    descricao: Mapped[str] = mapped_column(String(80), nullable=False)
    permite_fracionario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ErpLocalEstoque(SupabaseErpBase):
    __tablename__ = "locais_estoque"
    __table_args__ = {"schema": "erp"}

    local_estoque_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    filial_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ErpProduto(SupabaseErpBase):
    __tablename__ = "produtos"
    __table_args__ = {"schema": "erp"}

    produto_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sku: Mapped[str | None] = mapped_column(String(80))
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao_original: Mapped[str | None] = mapped_column(Text)
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("erp.marcas.marca_id"))
    unidade_medida_id: Mapped[int] = mapped_column(ForeignKey("erp.unidades_medida.unidade_medida_id"))
    tipo_item: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    origem_linha_excel: Mapped[int | None]

    marca: Mapped["ErpMarca | None"] = relationship()
    unidade: Mapped["ErpUnidadeMedida"] = relationship()
    precos: Mapped[list["ErpPrecoProduto"]] = relationship(back_populates="produto")
    saldos: Mapped[list["ErpEstoqueSaldo"]] = relationship(back_populates="produto")


class ErpPrecoProduto(SupabaseErpBase):
    __tablename__ = "precos_produto"
    __table_args__ = {"schema": "erp"}

    preco_produto_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("erp.produtos.produto_id"))
    tabela_preco: Mapped[str] = mapped_column(String(40), nullable=False)
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    inicio_vigencia: Mapped[Date] = mapped_column(Date, nullable=False)
    fim_vigencia: Mapped[Date | None] = mapped_column(Date)
    origem_linha_excel: Mapped[int | None]

    produto: Mapped["ErpProduto"] = relationship(back_populates="precos")


class ErpEstoqueSaldo(SupabaseErpBase):
    __tablename__ = "estoque_saldos"
    __table_args__ = {"schema": "erp"}

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("erp.produtos.produto_id"),
        primary_key=True,
    )
    local_estoque_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    alocacao: Mapped[str | None] = mapped_column(Text)
    observacao_alocacao: Mapped[str | None] = mapped_column(Text)

    produto: Mapped["ErpProduto"] = relationship(back_populates="saldos")
