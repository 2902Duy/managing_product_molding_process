from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.models.orm import Inventory
from backend.models.schemas import InventoryCreate, InventoryUpdate, InventoryResponse
from backend.services import db_crud

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryResponse])
async def list_inventory(
    type: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await db_crud.get_inventory(db, type_filter=type, status_filter=status)


@router.get("/search", response_model=list[InventoryResponse])
async def search_inventory(q: str = Query(""), db: AsyncSession = Depends(get_db)):
    if not q:
        return await db_crud.get_inventory(db)
    return await db_crud.search_inventory(db, q)


@router.get("/stats")
async def inventory_stats(db: AsyncSession = Depends(get_db)):
    stmt = select(
        Inventory.type,
        func.count(Inventory.id).label("count"),
        func.sum(Inventory.quantity).label("total_quantity"),
        func.sum(Inventory.volume).label("total_volume"),
    ).group_by(Inventory.type)
    result = await db.execute(stmt)
    stats = []
    for row in result.all():
        stats.append({
            "type": row.type,
            "count": row.count,
            "total_quantity": row.total_quantity or 0,
            "total_volume": float(row.total_volume or 0),
        })
    return stats


@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(item_id: str, db: AsyncSession = Depends(get_db)):
    item = await db_crud.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.post("", response_model=InventoryResponse, status_code=201)
async def create_inventory_item(payload: InventoryCreate, db: AsyncSession = Depends(get_db)):
    item_data = payload.model_dump(exclude_none=True)
    if "id" not in item_data or not item_data["id"]:
        import time, random
        item_data["id"] = f"INV-{int(time.time())}-{random.randint(100, 999)}"
    return await db_crud.create_inventory_item(db, item_data)


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(item_id: str, payload: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    item_data = payload.model_dump(exclude_none=True)
    item = await db_crud.update_inventory_item(db, item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: str, db: AsyncSession = Depends(get_db)):
    success = await db_crud.delete_inventory_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"detail": "Deleted"}


@router.patch("/{item_id}/status")
async def update_item_status(item_id: str, status: str = Query(...), db: AsyncSession = Depends(get_db)):
    item = await db_crud.update_inventory_item(db, item_id, {"status": status})
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"id": item_id, "status": status}


@router.patch("/{item_id}/quantity")
async def update_item_quantity(item_id: str, quantity: int = Query(...), db: AsyncSession = Depends(get_db)):
    item = await db_crud.update_inventory_item(db, item_id, {"quantity": quantity})
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"id": item_id, "quantity": quantity}


class BulkStatusUpdate(InventoryUpdate):
    ids: list[str]
    status: str  # type: ignore[assignment]


@router.post("/bulk-update-status")
async def bulk_update_status(
    ids: list[str] = Query(...),
    status: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    count = await db_crud.bulk_update_inventory_status(db, ids, status)
    return {"updated": count}
