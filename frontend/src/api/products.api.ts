import api from './axios'
import type { Product, ProductCard, ProductCreate, ProductUpdate, ProductFilters, PaginatedResponse } from '@/types/products'

function buildQueryString(filters: ProductFilters): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })
  return params.toString()
}

export const productsApi = {
  getProducts: async (filters: ProductFilters = {}): Promise<PaginatedResponse<ProductCard>> => {
    const queryString = buildQueryString(filters)
    const response = await api.get(`/products/?${queryString}`)
    return response.data
  },

  getMyProducts: async (): Promise<ProductCard[]> => {
    const response = await api.get('/products/me')
    return response.data
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/products/${id}`)
    return response.data
  },

  createProduct: async (data: ProductCreate): Promise<Product> => {
    const response = await api.post('/products/', data)
    return response.data
  },

  updateProduct: async (id: number, data: ProductUpdate): Promise<Product> => {
    const response = await api.patch(`/products/${id}`, data)
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`)
  },

  uploadImage: async (productId: number, file: File): Promise<{ id: number; image_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`/products/${productId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  deleteImage: async (productId: number, imageId: number): Promise<void> => {
    await api.delete(`/products/${productId}/images/${imageId}`)
  },
}
