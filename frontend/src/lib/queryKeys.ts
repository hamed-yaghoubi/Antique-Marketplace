import type { QueryClient } from '@tanstack/react-query'
import type { ProductFilters } from '@/types/products'
import type { OrderFilters } from '@/types/orders'

// IMPORTANT: query keys are organized as a parent/child tree so that
// invalidating a root key (e.g. ['products']) cascades to ALL child queries
// (lists, details, dashboards, etc.). TanStack Query matches by key prefix,
// so detail keys MUST be nested under their root — using sibling prefixes
// (e.g. ['product', id] next to ['products']) is a bug that silently breaks
// cache invalidation after mutations.

export const queryKeys = {
  products: {
    // Root key — invalidating this refreshes every product query.
    all: ['products'] as const,
    list: (filters: ProductFilters) => ['products', 'list', filters] as const,
    detail: (id: number) => ['products', 'detail', id] as const,
    myProducts: ['products', 'mine'] as const,
    adminList: (filters: ProductFilters) => ['products', 'admin', filters] as const,
    userProducts: (userId: number) => ['products', 'user', userId] as const,
  },
  cart: {
    all: ['cart'] as const,
  },
  orders: {
    // Root key — invalidating this refreshes every order query.
    all: ['orders'] as const,
    list: (filters: OrderFilters) => ['orders', 'list', filters] as const,
    detail: (id: number) => ['orders', 'detail', id] as const,
    stats: ['orders', 'stats'] as const,
    dashboard: ['orders', 'dashboard'] as const,
    sellerList: (filters: OrderFilters) => ['orders', 'seller', filters] as const,
    adminList: (filters: OrderFilters) => ['orders', 'admin', filters] as const,
    customerRecent: ['orders', 'customer-recent'] as const,
    customerStats: ['orders', 'customer-stats'] as const,
    sellerRecent: ['orders', 'seller-recent'] as const,
    sellerDashboard: ['orders', 'seller-dashboard'] as const,
    adminRecent: ['orders', 'admin-recent'] as const,
    adminDashboard: ['orders', 'admin-dashboard'] as const,
  },
  users: {
    // Root key — invalidating this refreshes every user query.
    all: ['users'] as const,
    detail: (id: number) => ['users', 'detail', id] as const,
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
