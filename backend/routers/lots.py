from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import (
    ProductionLotCreate, ProductionLotUpdate, ProductionLotResponse,
    LotInputResponse, LotOutputResponse, LotOutputCreate,
    ConsumeMaterialRequest, ReleaseMaterialRequest,
    LotTargetCreate, LotTargetResponse,
)
from backend.services import db_crud

router = APIRouter(prefix="/api/v1/lots", tags=["lots"])


@router.get("", response_model=list[ProductionLotResponse])
async def list_lots(
    slip_type: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    lots = await db_crud.get_lots(db, slip_type=slip_type, status=status)
    return lots


@router.get("/{lot_id}", response_model=ProductionLotResponse)
async def get_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    lot = await db_crud.get_lot(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return lot


@router.post("", response_model=ProductionLotResponse, status_code=201)
async def create_lot(payload: ProductionLotCreate, db: AsyncSession = Depends(get_db)):
    lot_data = payload.model_dump(exclude_none=True)
    if "id" not in lot_data or not lot_data["id"]:
        import time, random
        lot_data["id"] = f"LSX-{int(time.time())}-{random.randint(100, 999)}"
    if "created_date" not in lot_data:
        lot_data["created_date"] = date.today()
    lot = await db_crud.create_lot(db, lot_data)
    return lot


@router.put("/{lot_id}", response_model=ProductionLotResponse)
async def update_lot(lot_id: str, payload: ProductionLotUpdate, db: AsyncSession = Depends(get_db)):
    lot_data = payload.model_dump(exclude_none=True)
    lot = await db_crud.update_lot(db, lot_id, lot_data)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return lot


@router.delete("/{lot_id}")
async def delete_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    success = await db_crud.delete_lot(db, lot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lot not found")
    return {"detail": "Deleted"}


# ── Inputs ──

@router.get("/{lot_id}/inputs", response_model=list[LotInputResponse])
async def get_lot_inputs(lot_id: str, db: AsyncSession = Depends(get_db)):
    return await db_crud.get_lot_inputs(db, lot_id)


# ── Outputs ──

@router.get("/{lot_id}/outputs", response_model=list[LotOutputResponse])
async def get_lot_outputs(lot_id: str, db: AsyncSession = Depends(get_db)):
    return await db_crud.get_lot_outputs(db, lot_id)


@router.post("/{lot_id}/outputs", response_model=list[LotOutputResponse], status_code=201)
async def save_lot_outputs(lot_id: str, outputs: list[LotOutputCreate], db: AsyncSession = Depends(get_db)):
    await db_crud.delete_lot_outputs(db, lot_id)
    results = []
    for output in outputs:
        result = await db_crud.add_lot_output(db, lot_id, output.model_dump(exclude_none=True))
        results.append(result)
    return results


# ── Consume / Release Materials ──

@router.post("/{lot_id}/consume-materials")
async def consume_materials(
    lot_id: str,
    materials: list[ConsumeMaterialRequest],
    db: AsyncSession = Depends(get_db),
):
    lot = await db_crud.get_lot(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    results = []
    for mat in materials:
        inventory = await db_crud.get_inventory_item(db, mat.inventory_id)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory item {mat.inventory_id} not found")

        remaining = (inventory.quantity or 0) - mat.quantity_used
        new_status = "USED" if remaining <= 0 else "RESERVED"
        await db_crud.update_inventory_item(db, mat.inventory_id, {
            "status": new_status,
            "quantity": max(remaining, 0),
        })

        lot_input = await db_crud.add_lot_input(
            db, lot_id, mat.inventory_id, mat.quantity_used, mat.volume_used
        )
        results.append({
            "inventory_id": mat.inventory_id,
            "quantity_used": mat.quantity_used,
            "new_status": new_status,
        })

    return {"lot_id": lot_id, "consumed": results}


@router.post("/{lot_id}/release-materials")
async def release_materials(
    lot_id: str,
    materials: list[ReleaseMaterialRequest],
    db: AsyncSession = Depends(get_db),
):
    lot = await db_crud.get_lot(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    results = []
    for mat in materials:
        inventory = await db_crud.get_inventory_item(db, mat.inventory_id)
        if not inventory:
            continue

        restored_qty = (inventory.quantity or 0) + mat.quantity_used
        await db_crud.update_inventory_item(db, mat.inventory_id, {
            "status": "AVAILABLE",
            "quantity": restored_qty,
        })

        await db_crud.remove_lot_input(db, lot_id, mat.inventory_id)
        results.append({
            "inventory_id": mat.inventory_id,
            "restored_quantity": restored_qty,
        })

    return {"lot_id": lot_id, "released": results}


@router.get("/{lot_id}/material-usage")
async def get_material_usage(lot_id: str, db: AsyncSession = Depends(get_db)):
    inputs = await db_crud.get_lot_inputs(db, lot_id)
    usage = []
    for inp in inputs:
        inventory = await db_crud.get_inventory_item(db, inp.inventory_id)
        usage.append({
            "inventory_id": inp.inventory_id,
            "inventory_name": inventory.name if inventory else None,
            "quantity_used": inp.quantity_used,
            "volume_used": float(inp.volume_used) if inp.volume_used else None,
        })
    return {"lot_id": lot_id, "materials": usage}


# ── Lot Targets ──

@router.get("/{lot_id}/target", response_model=LotTargetResponse | None)
async def get_lot_target(lot_id: str, db: AsyncSession = Depends(get_db)):
    return await db_crud.get_lot_target(db, lot_id)


@router.post("/{lot_id}/target", response_model=LotTargetResponse)
async def set_lot_target(lot_id: str, payload: LotTargetCreate, db: AsyncSession = Depends(get_db)):
    target_data = payload.model_dump(exclude_none=True)
    return await db_crud.upsert_lot_target(db, lot_id, target_data)
