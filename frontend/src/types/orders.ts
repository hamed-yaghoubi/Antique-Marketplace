export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'shipped' | 'delivered' | 'cancelled'

export interface OrderItem {
  id: number
  product_id: number
  product_title: string
  unit_price: number
  quantity: number
}

export interface OrderResponse {
  id: number
  status: OrderStatus
  total_price: number
  created_at: string
  items: OrderItem[]
}

export interface OrderCard {
  id: number
  status: OrderStatus
  total_price: number
  created_at: string
  buyer_username: string | null
}

export interface OrderFilters {
  status?: OrderStatus
  search?: string
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  view?: 'buyer' | 'seller' | 'all'
  seller_id?: number
  buyer_id?: number
  date_from?: string
  date_to?: string
}

export interface PaginatedOrderResponse {
  items: OrderCard[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OrderStats {
  total: number
  pending: number
  confirmed: number
  preparing: number
  shipped: number
  delivered: number
  cancelled: number
}

export interface DashboardStats {
  order_stats: OrderStats
  total_products: number
  active_products: number
  out_of_stock_products: number
  total_users: number
  total_revenue: number
}

export const validStatusTransitions: Record<OrderStatus, OrderStatus[]> = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['preparing', 'cancelled'],
  preparing: ['shipped', 'cancelled'],
  shipped: ['delivered'],
  delivered: [],
  cancelled: [],
}

export function getValidTransitions(currentStatus: OrderStatus, isAdmin: boolean): OrderStatus[] {
  const buyerTransitions: Partial<Record<OrderStatus, OrderStatus[]>> = {
    pending: ['cancelled'],
  }

  if (isAdmin) {
    return validStatusTransitions[currentStatus]
  }

  return buyerTransitions[currentStatus] ?? []
}
