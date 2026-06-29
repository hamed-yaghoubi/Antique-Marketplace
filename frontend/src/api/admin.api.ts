import api from './axios'
import type { User } from '@/types/auth'

export const adminApi = {
  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/admin/products/${id}`)
  },

  getUsers: async (): Promise<User[]> => {
    const { data } = await api.get<User[]>('/admin/users')
    return data
  },

  updateUserRole: async (userId: number, role: 'user' | 'admin'): Promise<User> => {
    const { data } = await api.patch<User>(`/admin/users/${userId}/role`, { role })
    return data
  },

  banUser: async (userId: number): Promise<User> => {
    const { data } = await api.patch<User>(`/admin/users/${userId}/ban`)
    return data
  },

  unbanUser: async (userId: number): Promise<User> => {
    const { data } = await api.patch<User>(`/admin/users/${userId}/unban`)
    return data
  },
}
