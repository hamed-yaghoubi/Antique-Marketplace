import api from './axios'
import type { CartResponse, CartItemCreate, CartItemUpdate, CartItem } from '@/types/cart'

export const cartApi = {
  getCart: async (): Promise<CartResponse> => {
    const response = await api.get('/cart/')
    return response.data
  },

  addItem: async (data: CartItemCreate): Promise<CartItem> => {
    const response = await api.post('/cart/items', data)
    return response.data
  },

  updateItem: async (itemId: number, data: CartItemUpdate): Promise<CartItem> => {
    const response = await api.patch(`/cart/items/${itemId}`, data)
    return response.data
  },

  removeItem: async (itemId: number): Promise<void> => {
    await api.delete(`/cart/items/${itemId}`)
  },

  clearCart: async (): Promise<void> => {
    await api.delete('/cart/')
  },
}
