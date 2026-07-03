import api from './axios'
import type { User } from '@/types/auth'

export const adminApi = {
  getUser: async (userId: number): Promise<User> => {
    const response = await api.get<User>(`/admin/users/${userId}`)
    return response.data
  },

  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/admin/users')
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/admin/products/${id}`)
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

  demoteUser: async (userId: number): Promise<User> => {
    const response = await api.post<User>(`/owner/demote/${userId}`)
    return response.data
  },
}
