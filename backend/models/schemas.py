from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field


# ── Production Lots ──

class ProductionLotCreate(BaseModel):
    id: str | None = None
    name: str | None = None
    status: str = "Đang sản xuất"
    created_date: date | None = None
    slip_type: str = "PHOI_GO"
    description: str | None = None
    created_by: str | None = None
    data: dict[str, Any] | None = None


class ProductionLotUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    description: str | None = None
    slip_type: str | None = None
    data: dict[str, Any] | None = None


class ProductionLotResponse(BaseModel):
    id: str
    name: str | None = None
    status: str
    created_date: date
    slip_type: str
    description: str | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    data: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


# ── Inventory ──

class InventoryCreate(BaseModel):
    id: str | None = None
    name: str
    type: str = "RAW"
    length: int | None = None
    width: int | None = None
    thickness: int | None = None
    quantity: int = 0
    volume: float | None = None
    status: str = "AVAILABLE"
    source_lot_id: str | None = None
    wood_type: str | None = None
    batch_id: str | None = None


class InventoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    length: int | None = None
    width: int | None = None
    thickness: int | None = None
    quantity: int | None = None
    volume: float | None = None
    status: str | None = None
    source_lot_id: str | None = None
    wood_type: str | None = None
    batch_id: str | None = None


class InventoryResponse(BaseModel):
    id: str
    name: str
    type: str
    length: int | None = None
    width: int | None = None
    thickness: int | None = None
    quantity: int
    volume: float | None = None
    status: str | None = None
    source_lot_id: str | None = None
    wood_type: str | None = None
    batch_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Lot Inputs ──

class LotInputCreate(BaseModel):
    inventory_id: str
    quantity_used: int
    volume_used: float | None = None


class LotInputResponse(BaseModel):
    lot_id: str
    inventory_id: str
    quantity_used: int
    volume_used: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Lot Outputs ──

class LotOutputCreate(BaseModel):
    name: str
    length: int | None = None
    width: int | None = None
    thickness: int | None = None
    quantity: int | None = None
    volume: float
    status: str | None = None


class LotOutputResponse(BaseModel):
    id: int
    lot_id: str
    name: str
    length: int | None = None
    width: int | None = None
    thickness: int | None = None
    quantity: int | None = None
    volume: float
    status: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Orders ──

class OrderCreate(BaseModel):
    id: str | None = None
    name: str
    status: str | None = None
    created_date: date | None = None
    customer_name: str | None = None
    notes: str | None = None
    data: dict[str, Any] | None = None


class OrderResponse(BaseModel):
    id: str
    name: str
    status: str | None = None
    created_date: date | None = None
    customer_name: str | None = None
    notes: str | None = None
    data: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Lot Targets ──

class LotTargetCreate(BaseModel):
    order_id: str | None = None
    quantity_produce: int
    data: dict[str, Any] | None = None


class LotTargetResponse(BaseModel):
    lot_id: str
    order_id: str | None = None
    quantity_produce: int
    data: dict[str, Any] | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Material Operations ──

class ConsumeMaterialRequest(BaseModel):
    inventory_id: str
    quantity_used: int
    volume_used: float | None = None


class ReleaseMaterialRequest(BaseModel):
    inventory_id: str
    quantity_used: int
