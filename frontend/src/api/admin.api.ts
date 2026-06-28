import api from './axios'

export const adminApi = {
  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/admin/products/${id}`)
  },
}
