import api from './axios'
import type { Product, ProductFilters, PaginatedResponse, AdminProductCreate, AdminProductUpdate } from '@/types/products'

function buildQueryString(filters: ProductFilters): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })
  return params.toString()
}

export const adminApi = {
  getProducts: async (filters: ProductFilters = {}): Promise<PaginatedResponse<Product>> => {
    const queryString = buildQueryString(filters)
    const response = await api.get(`/admin/products?${queryString}`)
    return response.data
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/admin/products/${id}`)
    return response.data
  },

  createProduct: async (data: AdminProductCreate): Promise<Product> => {
    const response = await api.post('/admin/products', data)
    return response.data
  },

  updateProduct: async (id: number, data: AdminProductUpdate): Promise<Product> => {
    const response = await api.patch(`/admin/products/${id}`, data)
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/admin/products/${id}`)
  },
}
