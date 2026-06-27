export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'

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
}
