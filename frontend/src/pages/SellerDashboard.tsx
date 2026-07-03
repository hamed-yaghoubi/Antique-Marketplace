import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Package, TrendingUp, ShoppingCart, Plus, Clock, Truck, CheckCircle, XCircle, ExternalLink } from 'lucide-react'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Badge } from '@/components/ui/Badge'
import { CardSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import type { OrderStatus } from '@/types/orders'

const statusMap: Record<OrderStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'danger' | 'info' }> = {
  pending: { label: t.orders.pending, variant: 'warning' },
  confirmed: { label: t.orders.confirmed, variant: 'info' },
  preparing: { label: t.orders.preparing, variant: 'info' },
  shipped: { label: t.orders.shipped, variant: 'info' },
  delivered: { label: t.orders.delivered, variant: 'success' },
  cancelled: { label: t.orders.cancelled, variant: 'danger' },
}

export function SellerDashboard() {
  const { data: dashStats, isLoading: dashLoading } = useQuery({
    queryKey: ['seller-dashboard-stats'],
    queryFn: () => ordersApi.getDashboardStats(),
  })

  const { data: recentOrdersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['seller-recent-orders'],
    queryFn: () => ordersApi.getOrders({ page: 1, page_size: 5 }),
  })

  const isLoading = dashLoading || ordersLoading

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.dashboard.seller.title}</h1>
          <p className="mt-1 text-sm text-antique-sepia-light">{t.dashboard.seller.subtitle}</p>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  const orderStats = dashStats?.order_stats
  const outOfStock = (dashStats?.total_products ?? 0) - (dashStats?.active_products ?? 0)

  const productCards = [
    {
      label: t.dashboard.seller.totalProducts,
      value: toPersianNumbers(dashStats?.total_products ?? 0),
      icon: Package,
      color: 'text-antique-gold bg-antique-gold/10',
    },
    {
      label: t.dashboard.seller.activeProducts,
      value: toPersianNumbers(dashStats?.active_products ?? 0),
      icon: TrendingUp,
      color: 'text-green-700 bg-green-100',
    },
    {
      label: t.dashboard.seller.outOfStockProducts,
      value: toPersianNumbers(outOfStock),
      icon: ShoppingCart,
      color: 'text-red-700 bg-red-100',
    },
    {
      label: t.dashboard.seller.totalRevenue,
      value: formatPrice(Number(dashStats?.total_revenue ?? 0)),
      icon: TrendingUp,
      color: 'text-blue-700 bg-blue-100',
    },
  ]

  const orderStatCards = [
    { label: t.orders.pending, value: orderStats?.pending ?? 0, icon: Clock, color: 'text-amber-600 bg-amber-50' },
    { label: t.orders.preparing, value: orderStats?.preparing ?? 0, icon: Package, color: 'text-blue-600 bg-blue-50' },
    { label: t.orders.shipped, value: orderStats?.shipped ?? 0, icon: Truck, color: 'text-purple-600 bg-purple-50' },
    { label: t.orders.delivered, value: orderStats?.delivered ?? 0, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: t.orders.cancelled, value: orderStats?.cancelled ?? 0, icon: XCircle, color: 'text-red-600 bg-red-50' },
  ]

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.dashboard.seller.title}</h1>
        <p className="mt-1 text-sm text-antique-sepia-light">{t.dashboard.seller.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {productCards.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center gap-4">
              <div className={`rounded-xl p-3 ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-antique-sepia-light">{stat.label}</p>
                <p className="text-xl font-bold text-antique-wood">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6">
        <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.orders.stats.ordersByStatus}</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {orderStatCards.map((stat) => (
            <div key={stat.label} className="card">
              <div className="flex items-center gap-3">
                <div className={`rounded-lg p-2 ${stat.color}`}>
                  <stat.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm text-antique-sepia-light">{stat.label}</p>
                  <p className="text-lg font-bold text-antique-wood">{toPersianNumbers(stat.value)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.dashboard.recentOrders}</h2>
          {!recentOrdersData || recentOrdersData.items.length === 0 ? (
            <div className="card py-8 text-center">
              <p className="text-antique-sepia-light">{t.dashboard.noOrders}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentOrdersData.items.map((order) => {
                const status = statusMap[order.status] || { label: order.status, variant: 'default' as const }
                return (
                  <Link key={order.id} to="/seller/orders">
                    <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-antique-gold">#{toPersianNumbers(order.id)}</span>
                        <div>
                          <p className="text-sm font-medium text-antique-wood">{t.orders.orderNumber} {toPersianNumbers(order.id)}</p>
                          <p className="text-xs text-antique-sepia-light">{formatJalali(order.created_at)}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={status.variant}>{status.label}</Badge>
                        <span className="text-sm font-bold text-antique-gold">{formatPrice(order.total_price)}</span>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </div>

        <div>
          <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.dashboard.quickActions}</h2>
          <div className="space-y-3">
            <Link to="/my-products">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-antique-gold/10 p-2">
                    <Plus className="h-5 w-5 text-antique-gold" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.seller.createProduct}</span>
                </div>
                <ExternalLink className="h-4 w-4 text-antique-sepia-light" />
              </div>
            </Link>
            <Link to="/my-products">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-green-100 p-2">
                    <Package className="h-5 w-5 text-green-700" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.seller.manageProducts}</span>
                </div>
                <ExternalLink className="h-4 w-4 text-antique-sepia-light" />
              </div>
            </Link>
            <Link to="/seller/orders">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-100 p-2">
                    <ShoppingCart className="h-5 w-5 text-blue-700" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.seller.manageOrders}</span>
                </div>
                <ExternalLink className="h-4 w-4 text-antique-sepia-light" />
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
