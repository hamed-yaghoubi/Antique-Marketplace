export type ProductCategory = 'coin' | 'clock' | 'painting' | 'book' | 'statue'

export interface ProductImage {
  id: number
  image_url: string
}

export interface ProductCard {
  id: number
  title: string
  price: number
  category: ProductCategory
  is_active: boolean
  quantity: number
  seller_id: number
  seller: string | null
  main_image: ProductImage | null
}

export interface Product extends ProductCard {
  description: string
  quantity: number
  seller_id: number
  created_at: string
  images: ProductImage[]
}

export interface ProductCreate {
  title: string
  description: string
  price: number
  quantity: number
  category: ProductCategory
}

export interface ProductUpdate {
  title?: string
  description?: string
  price?: number
  quantity?: number
  category?: ProductCategory
  is_active?: boolean
}

export interface ProductFilters {
  search?: string
  category?: ProductCategory
  min_price?: number
  max_price?: number
  min_quantity?: number
  max_quantity?: number
  is_active?: boolean
  seller_id?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
