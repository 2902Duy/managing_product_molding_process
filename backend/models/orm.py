import enum
from datetime import date, datetime
from sqlalchemy import (
    String, Integer, Numeric, Text, Date, DateTime, Enum, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class SlipType(str, enum.Enum):
    PHOI_GO = "PHOI_GO"
    HOAN_THIEN = "HOAN_THIEN"


class LotStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    DANG_SAN_XUAT = "Đang sản xuất"
    HOAN_THANH = "Hoàn thành"


class InventoryType(str, enum.Enum):
    RAW = "RAW"
    SEMIFINISHED = "SEMIFINISHED"
    SURPLUS = "SURPLUS"
    WASTE = "WASTE"


class InventoryStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    USED = "USED"


class ProductionLot(Base):
    __tablename__ = "production_lots"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    created_date: Mapped[date] = mapped_column(Date, nullable=False)
    slip_type: Mapped[str] = mapped_column(String(20), nullable=False, default="PHOI_GO")
    description: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(100))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    data: Mapped[dict | None] = mapped_column(JSON)

    inputs: Mapped[list["LotInput"]] = relationship(back_populates="lot", cascade="all, delete-orphan")
    outputs: Mapped[list["LotOutput"]] = relationship(back_populates="lot", cascade="all, delete-orphan")
    target: Mapped["LotTarget | None"] = relationship(back_populates="lot", cascade="all, delete-orphan", uselist=False)


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="RAW")
    length: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    thickness: Mapped[int | None] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    volume: Mapped[float | None] = mapped_column(Numeric(10, 4))
    status: Mapped[str | None] = mapped_column(String(100), default="AVAILABLE")
    source_lot_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("production_lots.id"))
    wood_type: Mapped[str | None] = mapped_column(String(50))
    batch_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class LotInput(Base):
    __tablename__ = "lot_inputs"

    lot_id: Mapped[str] = mapped_column(String(50), ForeignKey("production_lots.id", ondelete="CASCADE"), primary_key=True)
    inventory_id: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id", ondelete="CASCADE"), primary_key=True)
    quantity_used: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_used: Mapped[float | None] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    lot: Mapped["ProductionLot"] = relationship(back_populates="inputs")


class LotOutput(Base):
    __tablename__ = "lot_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[str] = mapped_column(String(50), ForeignKey("production_lots.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    length: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    thickness: Mapped[int | None] = mapped_column(Integer)
    quantity: Mapped[int | None] = mapped_column(Integer)
    volume: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    status: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    lot: Mapped["ProductionLot"] = relationship(back_populates="outputs")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str | None] = mapped_column(String(50))
    created_date: Mapped[date | None] = mapped_column(Date, default=date.today)
    customer_name: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    data: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class LotTarget(Base):
    __tablename__ = "lot_targets"

    lot_id: Mapped[str] = mapped_column(String(50), ForeignKey("production_lots.id", ondelete="CASCADE"), primary_key=True)
    order_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("orders.id"))
    quantity_produce: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    lot: Mapped["ProductionLot"] = relationship(back_populates="target")
