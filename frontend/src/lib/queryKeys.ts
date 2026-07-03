import type { QueryClient } from '@tanstack/react-query'
import type { ProductFilters } from '@/types/products'
import type { OrderFilters } from '@/types/orders'

export const queryKeys = {
  products: {
    all: ['products'] as const,
    list: (filters: ProductFilters) => ['products', filters] as const,
    detail: (id: number) => ['product', id] as const,
    myProducts: ['my-products'] as const,
    adminList: (filters: ProductFilters) => ['admin-products', filters] as const,
    userProducts: (userId: number) => ['admin-user-products', userId] as const,
  },
  cart: {
    all: ['cart'] as const,
  },
  orders: {
    all: ['orders'] as const,
    list: (filters: OrderFilters) => ['orders', filters] as const,
    detail: (id: number) => ['order', id] as const,
    stats: ['order-stats'] as const,
    dashboard: ['dashboard-stats'] as const,
    sellerList: (filters: OrderFilters) => ['seller-orders', filters] as const,
    adminList: (filters: OrderFilters) => ['admin-orders', filters] as const,
    customerRecent: ['customer-orders'] as const,
    customerStats: ['customer-order-stats'] as const,
    sellerRecent: ['seller-recent-orders'] as const,
    sellerDashboard: ['seller-dashboard-stats'] as const,
    adminRecent: ['admin-recent-orders'] as const,
    adminDashboard: ['admin-dashboard-stats'] as const,
  },
  users: {
    all: ['admin-users'] as const,
    detail: (id: number) => ['admin-user', id] as const,
  },
} as const

export function invalidateProducts(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.products.all })
}

export function invalidateProductDetail(qc: QueryClient, id: number) {
  qc.invalidateQueries({ queryKey: queryKeys.products.detail(id) })
}

export function invalidateMyProducts(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.products.myProducts })
}

export function invalidateCart(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.cart.all })
}

export function invalidateOrders(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.orders.all })
}

export function invalidateDashboards(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.orders.sellerDashboard })
  qc.invalidateQueries({ queryKey: queryKeys.orders.adminDashboard })
  qc.invalidateQueries({ queryKey: queryKeys.orders.customerStats })
  qc.invalidateQueries({ queryKey: queryKeys.orders.customerRecent })
  qc.invalidateQueries({ queryKey: queryKeys.orders.sellerRecent })
  qc.invalidateQueries({ queryKey: queryKeys.orders.adminRecent })
}

export function invalidateUsers(qc: QueryClient) {
  qc.invalidateQueries({ queryKey: queryKeys.users.all })
}
