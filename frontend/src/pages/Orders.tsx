import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, ChevronLeft, ChevronRight, ListOrdered } from 'lucide-react'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import { queryKeys } from '@/lib/queryKeys'
import type { OrderStatus, OrderFilters } from '@/types/orders'

const statusOptions: Array<{ value: OrderStatus; label: string }> = [
  { value: 'pending', label: t.orders.pending },
  { value: 'confirmed', label: t.orders.confirmed },
  { value: 'preparing', label: t.orders.preparing },
  { value: 'shipped', label: t.orders.shipped },
  { value: 'delivered', label: t.orders.delivered },
  { value: 'cancelled', label: t.orders.cancelled },
]

const statusMap: Record<OrderStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'danger' | 'info' }> = {
  pending: { label: t.orders.pending, variant: 'warning' },
  confirmed: { label: t.orders.confirmed, variant: 'info' },
  preparing: { label: t.orders.preparing, variant: 'info' },
  shipped: { label: t.orders.shipped, variant: 'info' },
  delivered: { label: t.orders.delivered, variant: 'success' },
  cancelled: { label: t.orders.cancelled, variant: 'danger' },
}

export function Orders() {
  const [filters, setFilters] = useState<OrderFilters>({ page: 1, page_size: 10 })

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.orders.list(filters),
    queryFn: () => ordersApi.getOrders(filters),
  })

  const updateFilter = (key: keyof OrderFilters, value: string | number | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>
        <LoadingSkeleton rows={4} />
      </div>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>
        <div className="mb-4 flex flex-wrap gap-3">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia" />
              <input
                type="text"
                placeholder={t.orders.searchOrders}
                className="input-field pr-10"
                value={filters.search || ''}
                onChange={(e) => updateFilter('search', e.target.value || undefined)}
              />
            </div>
          </div>
          <select
            className="input-field w-auto"
            value={filters.status || ''}
            onChange={(e) => updateFilter('status', (e.target.value as OrderStatus) || undefined)}
          >
            <option value="">{t.orders.allStatuses}</option>
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
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

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia" />
            <input
              type="text"
              placeholder={t.orders.searchOrders}
              className="input-field pr-10"
              value={filters.search || ''}
              onChange={(e) => updateFilter('search', e.target.value || undefined)}
            />
          </div>
        </div>
        <select
          className="input-field w-auto"
          value={filters.status || ''}
          onChange={(e) => updateFilter('status', (e.target.value as OrderStatus) || undefined)}
        >
          <option value="">{t.orders.allStatuses}</option>
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {data.items.map((order) => {
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

      {data.total_pages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-antique-sepia-light">
            {t.products.page} {toPersianNumbers(data.page)} {t.products.of} {toPersianNumbers(data.total_pages)} ({toPersianNumbers(data.total)} مورد)
          </p>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" disabled={data.page >= data.total_pages} onClick={() => updateFilter('page', data.page + 1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button variant="secondary" size="sm" disabled={data.page <= 1} onClick={() => updateFilter('page', data.page - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
