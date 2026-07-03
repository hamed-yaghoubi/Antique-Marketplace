import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ShoppingCart, Clock, CheckCircle, XCircle, Package, ListOrdered, ExternalLink } from 'lucide-react'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Badge } from '@/components/ui/Badge'
import { CardSkeleton } from '@/components/ui/LoadingSkeleton'
import { useAuth } from '@/contexts/AuthContext'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import { queryKeys } from '@/lib/queryKeys'
import type { OrderStatus } from '@/types/orders'

const statusMap: Record<OrderStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'danger' | 'info' }> = {
  pending: { label: t.orders.pending, variant: 'warning' },
  confirmed: { label: t.orders.confirmed, variant: 'info' },
  preparing: { label: t.orders.preparing, variant: 'info' },
  shipped: { label: t.orders.shipped, variant: 'info' },
  delivered: { label: t.orders.delivered, variant: 'success' },
  cancelled: { label: t.orders.cancelled, variant: 'danger' },
}

export function CustomerDashboard() {
  const { user } = useAuth()

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: queryKeys.orders.customerRecent,
    queryFn: () => ordersApi.getOrders({ page: 1, page_size: 5, view: 'buyer' }),
  })

  const { data: orderStats, isLoading: statsLoading } = useQuery({
    queryKey: queryKeys.orders.customerStats,
    queryFn: ordersApi.getOrderStats,
  })

  const isLoading = ordersLoading || statsLoading

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.dashboard.customer.title}</h1>
          <p className="mt-1 text-sm text-antique-sepia-light">{t.dashboard.customer.subtitle}</p>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  const orderStatCards = [
    { label: t.dashboard.customer.totalOrders, value: orderStats?.total ?? 0, icon: Package, color: 'text-antique-gold bg-antique-gold/10' },
    { label: t.dashboard.customer.pendingOrders, value: orderStats?.pending ?? 0, icon: Clock, color: 'text-amber-600 bg-amber-50' },
    { label: t.dashboard.customer.deliveredOrders, value: orderStats?.delivered ?? 0, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: t.dashboard.customer.cancelledOrders, value: orderStats?.cancelled ?? 0, icon: XCircle, color: 'text-red-600 bg-red-50' },
  ]

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">
          {t.dashboard.welcome}، {user?.username}
        </h1>
        <p className="mt-1 text-sm text-antique-sepia-light">{t.dashboard.customer.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {orderStatCards.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center gap-4">
              <div className={`rounded-xl p-3 ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-antique-sepia-light">{stat.label}</p>
                <p className="text-xl font-bold text-antique-wood">{toPersianNumbers(stat.value)}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.dashboard.recentOrders}</h2>
          {!ordersData || ordersData.items.length === 0 ? (
            <div className="card py-8 text-center">
              <ListOrdered className="mx-auto h-12 w-12 text-antique-gold/30" />
              <p className="mt-3 text-antique-sepia-light">{t.dashboard.noOrders}</p>
              <Link to="/" className="mt-3 inline-block text-sm font-medium text-antique-gold hover:underline">
                {t.dashboard.customer.browseProducts}
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {ordersData.items.map((order) => {
                const status = statusMap[order.status] || { label: order.status, variant: 'default' as const }
                return (
                  <Link key={order.id} to={`/orders/${order.id}`}>
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
            <Link to="/">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-antique-gold/10 p-2">
                    <Package className="h-5 w-5 text-antique-gold" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.customer.browseProducts}</span>
                </div>
                <ExternalLink className="h-4 w-4 text-antique-sepia-light" />
              </div>
            </Link>
            <Link to="/orders">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-100 p-2">
                    <ListOrdered className="h-5 w-5 text-blue-700" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.customer.myOrders}</span>
                </div>
                <ExternalLink className="h-4 w-4 text-antique-sepia-light" />
              </div>
            </Link>
            <Link to="/cart">
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-green-100 p-2">
                    <ShoppingCart className="h-5 w-5 text-green-700" />
                  </div>
                  <span className="font-medium text-antique-wood">{t.dashboard.customer.shoppingCart}</span>
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
