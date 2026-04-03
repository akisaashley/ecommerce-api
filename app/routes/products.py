from fastapi import APIRouter, HTTPException, Query, status
from decimal import Decimal

from app.database.mysql_connector import execute_query
from app.models.product import ProductCreate, ProductResponse, StockCheckRequest, StockCheckResponse, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=dict)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_stock: int | None = Query(None, ge=0),
    search: str | None = Query(None),
):
    params = []
    where_clause = "WHERE 1=1"

    if min_stock is not None:
        where_clause += " AND stock_quantity >= %s"
        params.append(min_stock)

    if search:
        where_clause += " AND (name LIKE %s OR sku LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM products {where_clause}"
    total_result = execute_query(count_query, tuple(params), fetch_one=True)
    total = total_result["total"] if total_result else 0

    # Get paginated results
    query = f"""
        SELECT id, sku, name, description, price, stock_quantity, created_at, updated_at
        FROM products
        {where_clause}
        ORDER BY id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, skip])
    products = execute_query(query, tuple(params), fetch_all=True) or []

    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": products,
    }


@router.get("/{product_id}", response_model=dict)
def get_product(product_id: int):
    product = execute_query(
        "SELECT id, sku, name, description, price, stock_quantity, created_at, updated_at FROM products WHERE id = %s",
        (product_id,),
        fetch_one=True,
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"success": True, "data": product}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate):
    # Check if SKU already exists
    existing = execute_query(
        "SELECT id FROM products WHERE sku = %s",
        (payload.sku,),
        fetch_one=True,
    )
    if existing:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    execute_query(
        """
        INSERT INTO products (sku, name, description, price, stock_quantity)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (payload.sku, payload.name, payload.description, payload.price, payload.stock_quantity),
        commit=True,
    )

    product = execute_query(
        "SELECT id, sku, name, description, price, stock_quantity, created_at, updated_at FROM products WHERE sku = %s",
        (payload.sku,),
        fetch_one=True,
    )

    return {"success": True, "message": "Product created successfully", "data": product}


@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdate):
    existing = execute_query(
        "SELECT id FROM products WHERE id = %s",
        (product_id,),
        fetch_one=True,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    updates = []
    params = []

    if payload.sku is not None:
        updates.append("sku = %s")
        params.append(payload.sku)
    if payload.name is not None:
        updates.append("name = %s")
        params.append(payload.name)
    if payload.description is not None:
        updates.append("description = %s")
        params.append(payload.description)
    if payload.price is not None:
        updates.append("price = %s")
        params.append(payload.price)
    if payload.stock_quantity is not None:
        updates.append("stock_quantity = %s")
        params.append(payload.stock_quantity)

    if updates:
        params.append(product_id)
        execute_query(
            f"UPDATE products SET {', '.join(updates)} WHERE id = %s",
            tuple(params),
            commit=True,
        )

    product = execute_query(
        "SELECT id, sku, name, description, price, stock_quantity, created_at, updated_at FROM products WHERE id = %s",
        (product_id,),
        fetch_one=True,
    )

    return {"success": True, "message": "Product updated successfully", "data": product}


@router.post("/{product_id}/check-stock", response_model=dict)
def check_stock(product_id: int, request: StockCheckRequest):
    product = execute_query(
        "SELECT id, stock_quantity FROM products WHERE id = %s",
        (product_id,),
        fetch_one=True,
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    is_available = product["stock_quantity"] >= request.quantity

    return {
        "success": True,
        "data": {
            "product_id": product_id,
            "requested_quantity": request.quantity,
            "available_quantity": product["stock_quantity"],
            "is_available": is_available,
        },
    }


@router.delete("/{product_id}")
def delete_product(product_id: int):
    existing = execute_query(
        "SELECT id FROM products WHERE id = %s",
        (product_id,),
        fetch_one=True,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    execute_query("DELETE FROM products WHERE id = %s", (product_id,), commit=True)

    return {"success": True, "message": "Product deleted successfully"}