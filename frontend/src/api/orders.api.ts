import api from './axios'
import type { OrderCard, OrderResponse } from '@/types/orders'

export const ordersApi = {
  getOrders: async (): Promise<OrderCard[]> => {
    const response = await api.get('/orders/')
    return response.data
  },

  getOrder: async (id: number): Promise<OrderResponse> => {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },

  createOrder: async (): Promise<OrderResponse> => {
    const response = await api.post('/orders/')
    return response.data
  },

  cancelOrder: async (id: number): Promise<OrderResponse> => {
    const response = await api.patch(`/orders/${id}/status`, { status: 'cancelled' })
    return response.data
  },
}
