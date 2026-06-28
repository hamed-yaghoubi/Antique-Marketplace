import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice, formatJalaliDateTime } from '@/utils/persian'
import type { OrderStatus } from '@/types/orders'

const statusMap: Record<OrderStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'danger' | 'info' }> = {
  pending: { label: t.orders.pending, variant: 'warning' },
  confirmed: { label: t.orders.confirmed, variant: 'info' },
  shipped: { label: t.orders.shipped, variant: 'info' },
  delivered: { label: t.orders.delivered, variant: 'success' },
  cancelled: { label: t.orders.cancelled, variant: 'danger' },
}

export function OrderDetail() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [showCancelModal, setShowCancelModal] = useState(false)

  const { data: order, isLoading, error } = useQuery({
    queryKey: ['order', id],
    queryFn: () => ordersApi.getOrder(Number(id)),
    enabled: !!id,
  })

  const cancelMutation = useMutation({
    mutationFn: () => ordersApi.cancelOrder(Number(id)),
    onSuccess: () => {
      toast.success(t.orders.cancelSuccess)
      queryClient.invalidateQueries({ queryKey: ['order', id] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['my-products'] })
      setShowCancelModal(false)
    },
    onError: (error: Error) => {
      toast.error(error.message || t.orders.cancelFailed)
      setShowCancelModal(false)
    },
  })

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <LoadingSkeleton rows={6} />
      </div>
    )
  }

  if (error || !order) {
    return (
      <div>
        <Breadcrumbs />
        <div className="card py-16 text-center">
          <p className="text-lg font-semibold text-antique-wood">{t.common.error}</p>
          <Link to="/orders" className="mt-4 inline-block">
            <Button variant="secondary">{t.orders.title}</Button>
          </Link>
        </div>
      </div>
    )
  }

  const status = statusMap[order.status] || { label: order.status, variant: 'default' as const }
  const canCancel = order.status === 'pending'

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-4">
        <Link to="/orders" className="inline-flex items-center gap-2 text-sm text-antique-sepia-light hover:text-antique-gold transition-colors">
          <ArrowRight className="h-4 w-4" />
          {t.orders.title}
        </Link>
      </div>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">
            {t.orders.orderNumber} {toPersianNumbers(order.id)}
          </h1>
          <p className="mt-1 text-sm text-antique-sepia-light">{formatJalaliDateTime(order.created_at)}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={status.variant}>{status.label}</Badge>
          {canCancel && (
            <Button variant="danger" size="sm" onClick={() => setShowCancelModal(true)}>
              {t.orders.cancelOrder}
            </Button>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.orders.items}</h2>
        <div className="divide-y divide-antique-gold/10">
          {order.items.map((item) => (
            <div key={item.id} className="flex items-center justify-between py-4">
              <div>
                <p className="font-semibold text-antique-wood">{item.product_title}</p>
                <p className="text-sm text-antique-sepia-light">
                  {toPersianNumbers(item.quantity)} × {formatPrice(item.unit_price)}
                </p>
              </div>
              <p className="font-bold text-antique-wood">{formatPrice(item.unit_price * item.quantity)}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 border-t-2 border-antique-gold/20 pt-4">
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-antique-wood">{t.orders.total}</span>
            <span className="text-2xl font-bold text-antique-gold">{formatPrice(order.total_price)}</span>
          </div>
        </div>
      </div>

      <Modal isOpen={showCancelModal} onClose={() => setShowCancelModal(false)} title={t.orders.cancelOrder} size="sm">
        <p className="text-sm text-antique-sepia-light">{t.orders.cancelConfirm}</p>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowCancelModal(false)}>{t.common.cancel}</Button>
          <Button variant="danger" isLoading={cancelMutation.isPending} onClick={() => cancelMutation.mutate()}>
            {t.orders.cancelOrder}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
