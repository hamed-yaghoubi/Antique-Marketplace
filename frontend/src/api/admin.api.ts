import api from './axios'
import type { User } from '@/types/auth'

export const adminApi = {
  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/admin/products/${id}`)
  },

  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/admin/users')
    return response.data
  },

  updateUserRole: async (userId: number, role: 'user' | 'admin'): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${userId}/role`, { role })
    return response.data
  },

  banUser: async (userId: number): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${userId}/ban`)
    return response.data
  },

  unbanUser: async (userId: number): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${userId}/unban`)
    return response.data
  },

  promoteUser: async (userId: number): Promise<User> => {
    const response = await api.post<User>(`/owner/promote/${userId}`)
    return response.data
  },
}
