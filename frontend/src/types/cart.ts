import type { ProductCard } from './products'

export interface CartItem {
  id: number
  quantity: number
  product: ProductCard
}

export interface CartResponse {
  items: CartItem[]
  total_price: number
}

export interface CartItemCreate {
  product_id: number
  quantity: number
}

export interface CartItemUpdate {
  quantity: number
}
