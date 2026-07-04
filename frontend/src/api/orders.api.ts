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
      if (filters.view) params.append('view', filters.view)
      if (filters.seller_id) params.append('seller_id', String(filters.seller_id))
      if (filters.buyer_id) params.append('buyer_id', String(filters.buyer_id))
      if (filters.date_from) params.append('date_from', filters.date_from)
      if (filters.date_to) params.append('date_to', filters.date_to)
    }
    const response = await api.get('/orders/', { params })
    return response.data
  },

  getOrder: async (id: number, view?: 'buyer' | 'seller' | 'all'): Promise<OrderResponse> => {
    const params = new URLSearchParams()
    if (view) params.append('view', view)
    const response = await api.get(`/orders/${id}`, { params })
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
