import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Search, ChevronLeft, ChevronRight, ListOrdered, Eye, RefreshCw } from 'lucide-react'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import { queryKeys, invalidateOrders, invalidateDashboards } from '@/lib/queryKeys'
import type { OrderStatus, OrderFilters } from '@/types/orders'
import { getValidTransitions } from '@/types/orders'

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

export function AdminOrders() {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState<OrderFilters>({ page: 1, page_size: 10 })
  const [statusModalOrderId, setStatusModalOrderId] = useState<number | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<OrderStatus>('pending')
  const [currentOrderStatus, setCurrentOrderStatus] = useState<OrderStatus>('pending')

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.orders.adminList(filters),
    queryFn: () => ordersApi.getOrders({ ...filters, view: 'all' }),
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: OrderStatus }) =>
      ordersApi.updateOrderStatus(id, status),
    onSuccess: () => {
      toast.success(t.orders.management.statusUpdated)
      invalidateOrders(queryClient)
      invalidateDashboards(queryClient)
      setStatusModalOrderId(null)
    },
    onError: () => toast.error(t.orders.management.statusUpdateFailed),
  })

  const validStatuses = getValidTransitions(currentOrderStatus, true)

  const updateFilter = (key: keyof OrderFilters, value: string | number | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  const openStatusModal = (orderId: number, currentStatus: OrderStatus) => {
    setStatusModalOrderId(orderId)
    setCurrentOrderStatus(currentStatus)
    setSelectedStatus(currentStatus)
  }

  const confirmStatusUpdate = () => {
    if (statusModalOrderId) {
      statusMutation.mutate({ id: statusModalOrderId, status: selectedStatus })
    }
  }

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.orders.title}</h1>
          <p className="mt-1 text-sm text-antique-sepia-light">{t.orders.dashboard.recentOrders}</p>
        </div>
      </div>

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

      {isLoading ? (
        <TableSkeleton rows={5} cols={6} />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-antique-gold/20 bg-antique-gold/5">
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.orders.orderNumber}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.orders.buyer}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.orders.status}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.orders.total}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.orders.date}</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-antique-wood">{t.admin.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-antique-gold/10">
              {data?.items.map((order) => {
                const status = statusMap[order.status] || { label: order.status, variant: 'default' as const }
                return (
                  <tr key={order.id} className="transition-colors hover:bg-antique-gold/5">
                    <td className="px-6 py-4">
                      <span className="font-semibold text-antique-wood">#{toPersianNumbers(order.id)}</span>
                    </td>
                    <td className="px-6 py-4 text-sm text-antique-wood">{order.buyer_username}</td>
                    <td className="px-6 py-4">
                      <Badge variant={status.variant}>{status.label}</Badge>
                    </td>
                    <td className="px-6 py-4 text-sm font-bold text-antique-wood">{formatPrice(order.total_price)}</td>
                    <td className="px-6 py-4 text-sm text-antique-sepia-light">{formatJalali(order.created_at)}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/orders/${order.id}?from=admin`}
                          className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-antique-gold/10 hover:text-antique-gold transition-colors"
                        >
                          <Eye className="h-4 w-4" />
                        </Link>
                        <button
                          onClick={() => openStatusModal(order.id, order.status)}
                          className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-antique-gold/10 hover:text-antique-gold transition-colors"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <ListOrdered className="mx-auto h-12 w-12 text-antique-gold/30" />
                    <p className="mt-4 text-sm text-antique-sepia-light">{t.orders.empty}</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total_pages > 1 && (
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

      <Modal isOpen={statusModalOrderId !== null} onClose={() => setStatusModalOrderId(null)} title={t.orders.management.updateStatus} size="sm">
        <p className="mb-4 text-sm text-antique-sepia-light">{t.orders.management.confirmStatus}</p>
        <select
          className="input-field w-full"
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value as OrderStatus)}
        >
          <option value={currentOrderStatus}>{statusMap[currentOrderStatus].label}</option>
          {statusOptions
            .filter((opt) => validStatuses.includes(opt.value))
            .map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
        </select>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setStatusModalOrderId(null)}>{t.admin.cancel}</Button>
          <Button isLoading={statusMutation.isPending} onClick={confirmStatusUpdate}>
            {t.admin.update}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
