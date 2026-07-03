import api from './axios'
import type {
  OrderResponse,
  OrderFilters,
  PaginatedOrderResponse,
  OrderStats,
  DashboardStats,
  OrderStatus,
} from '@/types/orders'

export const ordersApi = {
  getOrders: async (filters?: OrderFilters): Promise<PaginatedOrderResponse> => {
    const params = new URLSearchParams()
    if (filters) {
      if (filters.status) params.append('status', filters.status)
      if (filters.search) params.append('search', filters.search)
      if (filters.page) params.append('page', String(filters.page))
      if (filters.page_size) params.append('page_size', String(filters.page_size))
      if (filters.sort_by) params.append('sort_by', filters.sort_by)
      if (filters.sort_order) params.append('sort_order', filters.sort_order)
    }
    const response = await api.get('/orders/', { params })
    return response.data
  },

  getOrder: async (id: number): Promise<OrderResponse> => {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },

  getOrderStats: async (): Promise<OrderStats> => {
    const response = await api.get('/orders/stats')
    return response.data
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/orders/dashboard')
    return response.data
  },

  createOrder: async (): Promise<OrderResponse> => {
    const response = await api.post('/orders/')
    return response.data
  },

  updateOrderStatus: async (id: number, status: OrderStatus): Promise<OrderResponse> => {
    const response = await api.patch(`/orders/${id}/status`, { status })
    return response.data
  },

  cancelOrder: async (id: number): Promise<OrderResponse> => {
    const response = await api.patch(`/orders/${id}/status`, { status: 'cancelled' })
    return response.data
  },
}
