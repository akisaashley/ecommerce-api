from fastapi import APIRouter, HTTPException, Query, status
from decimal import Decimal
import uuid

from app.database.mysql_connector import execute_query, get_db_connection
from app.models.order import OrderCreate, OrderUpdate

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate):
    # Verify user exists
    user = execute_query(
        "SELECT id FROM users WHERE id = %s AND status = 'active'",
        (payload.user_id,),
        fetch_one=True,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order_uuid = str(uuid.uuid4())
    order_items = []
    total_amount = Decimal("0.00")

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Validate all products and calculate total
            for item in payload.items:
                product = execute_query(
                    "SELECT id, price, name, sku, stock_quantity FROM products WHERE id = %s AND status = 'active'",
                    (item.product_id,),
                    fetch_one=True,
                )
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

                if product["stock_quantity"] < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {product['name']}. Available: {product['stock_quantity']}"
                    )

                subtotal = Decimal(str(product["price"])) * item.quantity
                total_amount += subtotal

                order_items.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": product["price"],
                    "subtotal": subtotal,
                    "product_name": product["name"],
                    "product_sku": product["sku"],
                })

            # Create order
            execute_query(
                """
                INSERT INTO orders (order_uuid, user_id, total_amount, status)
                VALUES (%s, %s, %s, 'confirmed')
                """,
                (order_uuid, payload.user_id, total_amount),
                commit=True,
            )

            # Get the created order ID
            order = execute_query(
                "SELECT id FROM orders WHERE order_uuid = %s",
                (order_uuid,),
                fetch_one=True,
            )
            order_id = order["id"]

            # Create order items and update stock
            for item in order_items:
                execute_query(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (order_id, item["product_id"], item["quantity"], item["unit_price"], item["subtotal"]),
                    commit=True,
                )

                # Get current stock
                current_stock_result = execute_query(
                    "SELECT stock_quantity FROM products WHERE id = %s",
                    (item["product_id"],),
                    fetch_one=True,
                )
                previous_stock = current_stock_result["stock_quantity"]
                new_stock = previous_stock - item["quantity"]

                # Update stock
                execute_query(
                    "UPDATE products SET stock_quantity = %s WHERE id = %s",
                    (new_stock, item["product_id"]),
                    commit=True,
                )

                # Log inventory transaction
                execute_query(
                    """
                    INSERT INTO inventory_transactions (product_id, transaction_type, quantity, previous_stock, new_stock)
                    VALUES (%s, 'stock_out', %s, %s, %s)
                    """,
                    (item["product_id"], item["quantity"], previous_stock, new_stock),
                    commit=True,
                )

            # Get complete order details
            order_details = execute_query(
                """
                SELECT id, order_uuid, user_id, total_amount, status, created_at, updated_at
                FROM orders WHERE id = %s
                """,
                (order_id,),
                fetch_one=True,
            )

            # Get order items
            items = execute_query(
                """
                SELECT oi.id, oi.product_id, oi.quantity, oi.unit_price, oi.subtotal,
                       p.name as product_name, p.sku as product_sku
                FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id = %s
                """,
                (order_id,),
                fetch_all=True,
            )

            order_details["items"] = items or []

            return {"success": True, "message": "Order created successfully", "data": order_details}

        except Exception as e:
            conn.rollback()
            raise e


@router.get("", response_model=dict)
def list_orders(
    user_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str | None = Query(None),
):
    params = []
    where_clause = "WHERE 1=1"

    if user_id:
        where_clause += " AND user_id = %s"
        params.append(user_id)

    if status_filter:
        where_clause += " AND status = %s"
        params.append(status_filter)

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM orders {where_clause}"
    total_result = execute_query(count_query, tuple(params), fetch_one=True)
    total = total_result["total"] if total_result else 0

    # Get paginated results
    query = f"""
        SELECT id, order_uuid, user_id, total_amount, status, created_at, updated_at
        FROM orders
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, skip])
    orders = execute_query(query, tuple(params), fetch_all=True) or []

    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": orders,
    }


@router.get("/{order_id}", response_model=dict)
def get_order(order_id: int):
    order = execute_query(
        """
        SELECT id, order_uuid, user_id, total_amount, status, created_at, updated_at
        FROM orders WHERE id = %s
        """,
        (order_id,),
        fetch_one=True,
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get order items
    items = execute_query(
        """
        SELECT oi.id, oi.product_id, oi.quantity, oi.unit_price, oi.subtotal,
               p.name as product_name, p.sku as product_sku
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = %s
        """,
        (order_id,),
        fetch_all=True,
    )

    order["items"] = items or []

    return {"success": True, "data": order}


@router.put("/{order_id}/status")
def update_order_status(order_id: int, payload: OrderUpdate):
    order = execute_query(
        "SELECT id FROM orders WHERE id = %s",
        (order_id,),
        fetch_one=True,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if payload.status:
        execute_query(
            "UPDATE orders SET status = %s WHERE id = %s",
            (payload.status.value, order_id),
            commit=True,
        )

    updated_order = execute_query(
        "SELECT id, order_uuid, user_id, total_amount, status, created_at, updated_at FROM orders WHERE id = %s",
        (order_id,),
        fetch_one=True,
    )

    return {"success": True, "message": "Order status updated", "data": updated_order}