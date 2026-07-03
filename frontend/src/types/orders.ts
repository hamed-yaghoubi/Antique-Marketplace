export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'shipped' | 'delivered' | 'cancelled'

export interface OrderItem {
  id: number
  product_id: number
  product_title: string
  unit_price: number
  quantity: number
  seller_id: number
  seller_name: string
  product_image_url: string
}

export interface OrderResponse {
  id: number
  status: OrderStatus
  total_price: number
  created_at: string
  updated_at: string
  buyer_username: string
  items: OrderItem[]
}

export interface OrderCard {
  id: number
  status: OrderStatus
  total_price: number
  created_at: string
  buyer_username: string
  item_count: number
}

export interface OrderFilters {
  status?: OrderStatus
  search?: string
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedOrderResponse {
  items: OrderCard[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OrderStats {
  total_orders: number
  total_revenue: number
  orders_by_status: Record<OrderStatus, number>
  average_order_value: number
}

export interface DashboardStats {
  order_stats: OrderStats
  total_products: number
  active_products: number
  total_users: number
  total_revenue: number
}
