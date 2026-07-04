from decimal import Decimal
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from src.orders.models import Order, OrderItem
from src.orders.schemas import OrderFilter, PaginationParams
from src.users.models import User
from src.products.models import Product


def get_by_id(db: Session, order_id: int) -> Order | None:
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items), selectinload(Order.buyer))
    )
    return db.execute(query).scalar_one_or_none()


def get_by_id_for_seller(db: Session, order_id: int, seller_id: int) -> Order | None:
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.buyer),
        )
    )
    order = db.execute(query).scalar_one_or_none()
    if order is None:
        return None
    order.items = [item for item in order.items if item.seller_id == seller_id]
    return order


def get_by_buyer_id(db: Session, buyer_id: int) -> list[Order]:
    query = (
        select(Order)
        .where(Order.buyer_id == buyer_id)
        .options(selectinload(Order.items))
    )
    result = db.execute(query).scalars().all()

    return result


def get_by_seller_id(db: Session, seller_id: int) -> list[Order]:
    query = (
        select(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .where(OrderItem.seller_id == seller_id)
        .options(selectinload(Order.items))
        .distinct()
    )
    result = db.execute(query).scalars().all()

    return result


def get_all(db: Session) -> list[Order]:
    query = (
        select(Order)
        .options(selectinload(Order.items))
    )
    return list(db.execute(query).scalars().all())


def order_contains_seller_product(db: Session, order_id: int, seller_id: int) -> bool:
    query = (
        select(func.count())
        .select_from(OrderItem)
        .where(OrderItem.order_id == order_id, OrderItem.seller_id == seller_id)
    )
    return db.execute(query).scalar() > 0


def get_filtered(
    db: Session,
    filters: OrderFilter,
    pagination: PaginationParams,
    seller_id: int | None = None,
    buyer_id: int | None = None,
) -> tuple[list[Order], int]:
    query = select(Order)

    if buyer_id is not None:
        query = query.where(Order.buyer_id == buyer_id)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.join(Order.buyer, isouter=True)
        term = filters.search.strip()
        conditions = [User.username.ilike(search_term)]
        # Only compare against the integer Order.id when the search term is
        # numeric. Comparing an integer column to a non-numeric string raises
        # a DataError on PostgreSQL and crashes the request with a 500.
        if term.isdigit():
            conditions.append(Order.id == int(term))
        query = query.where(or_(*conditions))

    if filters.status is not None:
        query = query.where(Order.status == filters.status)

    if filters.buyer_id is not None:
        query = query.where(Order.buyer_id == filters.buyer_id)

    if filters.created_after is not None:
        query = query.where(Order.created_at >= filters.created_after)

    if filters.created_before is not None:
        query = query.where(Order.created_at <= filters.created_before)

    if seller_id is not None:
        query = query.join(OrderItem, OrderItem.order_id == Order.id).where(
            OrderItem.seller_id == seller_id
        )

    if filters.seller_id is not None and seller_id is None:
        query = query.join(OrderItem, OrderItem.order_id == Order.id).where(
            OrderItem.seller_id == filters.seller_id
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    allowed_sort_columns = {"created_at", "total_price", "status", "id"}
    sort_by = filters.sort_by if filters.sort_by in allowed_sort_columns else "created_at"
    sort_column = getattr(Order, sort_by)
    if filters.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    query = query.options(
        selectinload(Order.items),
        selectinload(Order.buyer),
    )

    if seller_id is not None or filters.seller_id is not None:
        query = query.distinct()

    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)

    orders = db.execute(query).scalars().unique().all()
    return list(orders), total


def get_order_stats(
    db: Session,
    seller_id: int | None = None,
    buyer_id: int | None = None,
) -> dict:
    base_query = select(func.count()).select_from(Order)

    if buyer_id is not None:
        base_query = base_query.where(Order.buyer_id == buyer_id)

    if seller_id is not None:
        base_query = (
            select(func.count(Order.id).distinct())
            .select_from(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(OrderItem.seller_id == seller_id)
        )

    total = db.execute(base_query).scalar() or 0

    stats = {"total": total}
    for status in [
        "pending", "confirmed", "preparing", "shipped", "delivered", "cancelled"
    ]:
        q = select(func.count()).select_from(Order).where(Order.status == status)
        if buyer_id is not None:
            q = q.where(Order.buyer_id == buyer_id)
        if seller_id is not None:
            q = (
                select(func.count(Order.id).distinct())
                .select_from(Order)
                .join(OrderItem, OrderItem.order_id == Order.id)
                .where(Order.status == status, OrderItem.seller_id == seller_id)
            )
        stats[status] = db.execute(q).scalar() or 0

    return stats


def get_dashboard_stats(
    db: Session,
    seller_id: int | None = None,
) -> dict:
    order_stats = get_order_stats(db, seller_id=seller_id)

    if seller_id is not None:
        total_products = db.execute(
            select(func.count()).select_from(Product).where(Product.seller_id == seller_id)
        ).scalar() or 0
        active_products = db.execute(
            select(func.count()).select_from(Product).where(
                Product.seller_id == seller_id, Product.is_active == True
            )
        ).scalar() or 0
        out_of_stock_products = db.execute(
            select(func.count()).select_from(Product).where(
                Product.seller_id == seller_id, Product.quantity <= 0
            )
        ).scalar() or 0
        total_users = 0

        seller_order_ids = (
            select(Order.id)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(
                OrderItem.seller_id == seller_id,
                Order.status.in_(["confirmed", "preparing", "shipped", "delivered"]),
            )
            .distinct()
            .subquery()
        )
        revenue_query = (
            select(func.coalesce(func.sum(Order.total_price), 0))
            .select_from(Order)
            .where(Order.id.in_(select(seller_order_ids.c.id)))
        )
        total_revenue = db.execute(revenue_query).scalar() or Decimal("0.00")
    else:
        total_products = db.execute(
            select(func.count()).select_from(Product)
        ).scalar() or 0
        active_products = db.execute(
            select(func.count()).select_from(Product).where(Product.is_active == True)
        ).scalar() or 0
        out_of_stock_products = db.execute(
            select(func.count()).select_from(Product).where(Product.quantity <= 0)
        ).scalar() or 0
        total_users = db.execute(
            select(func.count()).select_from(User)
        ).scalar() or 0

        revenue_query = (
            select(func.coalesce(func.sum(Order.total_price), 0))
            .select_from(Order)
            .where(
                Order.status.in_(["confirmed", "preparing", "shipped", "delivered"])
            )
        )
        total_revenue = db.execute(revenue_query).scalar() or Decimal("0.00")

    return {
        "order_stats": order_stats,
        "total_products": total_products,
        "active_products": active_products,
        "out_of_stock_products": out_of_stock_products,
        "total_users": total_users,
        "total_revenue": total_revenue,
    }


def create(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def update(db: Session, order: Order) -> Order:
    db.commit()
    db.refresh(order)

    return order