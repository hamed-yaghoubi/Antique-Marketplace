import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ListOrdered } from 'lucide-react'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import type { OrderStatus } from '@/types/orders'

const statusMap: Record<OrderStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'danger' | 'info' }> = {
  pending: { label: t.orders.pending, variant: 'warning' },
  confirmed: { label: t.orders.confirmed, variant: 'info' },
  shipped: { label: t.orders.shipped, variant: 'info' },
  delivered: { label: t.orders.delivered, variant: 'success' },
  cancelled: { label: t.orders.cancelled, variant: 'danger' },
}

export function Orders() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: ordersApi.getOrders,
  })

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>
        <LoadingSkeleton rows={4} />
      </div>
    )
  }

  if (!orders || orders.length === 0) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>
        <div className="card py-16 text-center">
          <ListOrdered className="mx-auto h-16 w-16 text-antique-gold/30" />
          <p className="mt-4 text-lg font-semibold text-antique-wood">{t.orders.empty}</p>
          <Link to="/" className="mt-4 inline-block">
            <Button variant="secondary">{t.cart.browseProducts}</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Breadcrumbs />
      <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>

      <div className="space-y-4">
        {orders.map((order) => {
          const status = statusMap[order.status] || { label: order.status, variant: 'default' as const }
          return (
            <Link key={order.id} to={`/orders/${order.id}`}>
              <div className="card flex items-center justify-between transition-all hover:shadow-vintage-lg">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-antique-gold/10">
                    <span className="text-sm font-bold text-antique-gold">#{toPersianNumbers(order.id)}</span>
                  </div>
                  <div>
                    <p className="font-semibold text-antique-wood">
                      {t.orders.orderNumber} {toPersianNumbers(order.id)}
                    </p>
                    <p className="text-sm text-antique-sepia-light">{formatJalali(order.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant={status.variant}>{status.label}</Badge>
                  <p className="text-lg font-bold text-antique-gold">{formatPrice(order.total_price)}</p>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
