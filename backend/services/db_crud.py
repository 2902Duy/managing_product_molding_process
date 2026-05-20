from datetime import date, datetime
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.orm import (
    ProductionLot, Inventory, LotInput, LotOutput, Order, LotTarget
)


# ═══════════════════════════════════════════════════
# Production Lots CRUD
# ═══════════════════════════════════════════════════

async def get_lots(
    db: AsyncSession,
    slip_type: str | None = None,
    status: str | None = None,
) -> list[ProductionLot]:
    stmt = select(ProductionLot).order_by(ProductionLot.created_date.desc())
    if slip_type:
        stmt = stmt.where(ProductionLot.slip_type == slip_type)
    if status:
        stmt = stmt.where(ProductionLot.status == status)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_lot(db: AsyncSession, lot_id: str) -> ProductionLot | None:
    return await db.get(ProductionLot, lot_id)


async def create_lot(db: AsyncSession, lot_data: dict) -> ProductionLot:
    if "created_date" not in lot_data or lot_data["created_date"] is None:
        lot_data["created_date"] = date.today()
    lot = ProductionLot(**lot_data)
    db.add(lot)
    await db.flush()
    return lot


async def update_lot(db: AsyncSession, lot_id: str, lot_data: dict) -> ProductionLot | None:
    lot = await db.get(ProductionLot, lot_id)
    if not lot:
        return None
    lot_data["updated_at"] = datetime.utcnow()
    for key, value in lot_data.items():
        if value is not None:
            setattr(lot, key, value)
    await db.flush()
    return lot


async def delete_lot(db: AsyncSession, lot_id: str) -> bool:
    lot = await db.get(ProductionLot, lot_id)
    if not lot:
        return False
    await db.delete(lot)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════
# Inventory CRUD
# ═══════════════════════════════════════════════════

async def get_inventory(
    db: AsyncSession,
    type_filter: str | None = None,
    status_filter: str | None = None,
) -> list[Inventory]:
    stmt = select(Inventory).order_by(Inventory.created_at.desc())
    if type_filter:
        stmt = stmt.where(Inventory.type == type_filter)
    if status_filter:
        stmt = stmt.where(Inventory.status == status_filter)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_inventory_item(db: AsyncSession, item_id: str) -> Inventory | None:
    return await db.get(Inventory, item_id)


async def create_inventory_item(db: AsyncSession, item_data: dict) -> Inventory:
    item = Inventory(**item_data)
    db.add(item)
    await db.flush()
    return item


async def update_inventory_item(db: AsyncSession, item_id: str, item_data: dict) -> Inventory | None:
    item = await db.get(Inventory, item_id)
    if not item:
        return None
    item_data["updated_at"] = datetime.utcnow()
    for key, value in item_data.items():
        if value is not None:
            setattr(item, key, value)
    await db.flush()
    return item


async def delete_inventory_item(db: AsyncSession, item_id: str) -> bool:
    item = await db.get(Inventory, item_id)
    if not item:
        return False
    await db.delete(item)
    await db.flush()
    return True


async def search_inventory(db: AsyncSession, query: str) -> list[Inventory]:
    stmt = select(Inventory).where(
        Inventory.name.ilike(f"%{query}%") | Inventory.id.ilike(f"%{query}%")
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def bulk_update_inventory_status(db: AsyncSession, ids: list[str], status: str) -> int:
    stmt = (
        update(Inventory)
        .where(Inventory.id.in_(ids))
        .values(status=status, updated_at=datetime.utcnow())
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


# ═══════════════════════════════════════════════════
# Lot Inputs / Outputs CRUD
# ═══════════════════════════════════════════════════

async def get_lot_inputs(db: AsyncSession, lot_id: str) -> list[LotInput]:
    stmt = select(LotInput).where(LotInput.lot_id == lot_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_lot_input(db: AsyncSession, lot_id: str, inventory_id: str, quantity_used: int, volume_used: float | None = None) -> LotInput:
    existing = await db.get(LotInput, (lot_id, inventory_id))
    if existing:
        existing.quantity_used += quantity_used
        if volume_used:
            existing.volume_used = (existing.volume_used or 0) + volume_used
        await db.flush()
        return existing
    lot_input = LotInput(
        lot_id=lot_id,
        inventory_id=inventory_id,
        quantity_used=quantity_used,
        volume_used=volume_used,
    )
    db.add(lot_input)
    await db.flush()
    return lot_input


async def remove_lot_input(db: AsyncSession, lot_id: str, inventory_id: str) -> bool:
    stmt = delete(LotInput).where(LotInput.lot_id == lot_id, LotInput.inventory_id == inventory_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def get_lot_outputs(db: AsyncSession, lot_id: str) -> list[LotOutput]:
    stmt = select(LotOutput).where(LotOutput.lot_id == lot_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_lot_output(db: AsyncSession, lot_id: str, output_data: dict) -> LotOutput:
    output = LotOutput(lot_id=lot_id, **output_data)
    db.add(output)
    await db.flush()
    return output


async def delete_lot_outputs(db: AsyncSession, lot_id: str) -> int:
    stmt = delete(LotOutput).where(LotOutput.lot_id == lot_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


# ═══════════════════════════════════════════════════
# Orders CRUD
# ═══════════════════════════════════════════════════

async def get_orders(db: AsyncSession) -> list[Order]:
    stmt = select(Order).order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_order(db: AsyncSession, order_id: str) -> Order | None:
    return await db.get(Order, order_id)


async def create_order(db: AsyncSession, order_data: dict) -> Order:
    order = Order(**order_data)
    db.add(order)
    await db.flush()
    return order


async def search_orders(db: AsyncSession, query: str) -> list[Order]:
    stmt = select(Order).where(
        Order.name.ilike(f"%{query}%") | Order.id.ilike(f"%{query}%")
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ═══════════════════════════════════════════════════
# Lot Targets CRUD
# ═══════════════════════════════════════════════════

async def get_lot_target(db: AsyncSession, lot_id: str) -> LotTarget | None:
    return await db.get(LotTarget, lot_id)


async def upsert_lot_target(db: AsyncSession, lot_id: str, target_data: dict) -> LotTarget:
    existing = await db.get(LotTarget, lot_id)
    if existing:
        for key, value in target_data.items():
            if value is not None:
                setattr(existing, key, value)
        await db.flush()
        return existing
    target = LotTarget(lot_id=lot_id, **target_data)
    db.add(target)
    await db.flush()
    return target
