from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import OrderCreate, OrderResponse
from backend.services import db_crud

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("", response_model=list[OrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    return await db_crud.get_orders(db)


@router.get("/search", response_model=list[OrderResponse])
async def search_orders(q: str = Query(""), db: AsyncSession = Depends(get_db)):
    if not q:
        return await db_crud.get_orders(db)
    return await db_crud.search_orders(db, q)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    order = await db_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    order_data = payload.model_dump(exclude_none=True)
    if "id" not in order_data or not order_data["id"]:
        import time, random
        order_data["id"] = f"DH-{int(time.time())}-{random.randint(100, 999)}"
    return await db_crud.create_order(db, order_data)
