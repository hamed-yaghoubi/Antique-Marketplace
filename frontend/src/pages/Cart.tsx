import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react'
import toast from 'react-hot-toast'
import { cartApi } from '@/api/cart.api'
import { ordersApi } from '@/api/orders.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice } from '@/utils/persian'

export function Cart() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: cartApi.getCart,
  })

  const updateMutation = useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: number; quantity: number }) =>
      cartApi.updateItem(itemId, { quantity }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
    onError: () => toast.error(t.cart.updateFailed),
  })

  const removeMutation = useMutation({
    mutationFn: (itemId: number) => cartApi.removeItem(itemId),
    onSuccess: () => {
      toast.success(t.cart.itemRemoved)
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
    onError: () => toast.error(t.cart.removeFailed),
  })

  const clearMutation = useMutation({
    mutationFn: () => cartApi.clearCart(),
    onSuccess: () => {
      toast.success(t.cart.cartCleared)
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
  })

  const checkoutMutation = useMutation({
    mutationFn: () => ordersApi.createOrder(),
    onSuccess: (order) => {
      toast.success(t.orders.createSuccess)
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['my-products'] })
      if (cart?.items) {
        for (const item of cart.items) {
          queryClient.invalidateQueries({ queryKey: ['product', item.product.id] })
        }
      }
      navigate(`/orders/${order.id}`)
    },
    onError: (error: Error) => {
      toast.error(error.message || t.orders.createFailed)
    },
  })

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.cart.title}</h1>
        <LoadingSkeleton rows={4} />
      </div>
    )
  }

  const items = cart?.items || []

  if (items.length === 0) {
    return (
      <div>
        <Breadcrumbs />
        <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.cart.title}</h1>
        <div className="card py-16 text-center">
          <ShoppingBag className="mx-auto h-16 w-16 text-antique-gold/30" />
          <p className="mt-4 text-lg font-semibold text-antique-wood">{t.cart.empty}</p>
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
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.cart.title}</h1>
        <Button variant="ghost" size="sm" onClick={() => clearMutation.mutate()}>
          <Trash2 className="h-4 w-4" />
          {t.cart.clearCart}
        </Button>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="card flex items-center gap-4">
            <div className="h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-antique-gold/5">
              {item.product.main_image ? (
                <img src={item.product.main_image.image_url} alt={item.product.title} className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  <span className="text-[10px] text-antique-sepia">{t.products.noImage}</span>
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <Link to={`/products/${item.product.id}`} className="font-semibold text-antique-wood hover:text-antique-gold transition-colors line-clamp-1">
                {item.product.title}
              </Link>
              <p className="text-sm text-antique-sepia-light">{formatPrice(item.product.price)}</p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => updateMutation.mutate({ itemId: item.id, quantity: Math.max(1, item.quantity - 1) })}
                className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-antique-gold/10 transition-colors"
              >
                <Minus className="h-4 w-4" />
              </button>
              <span className="w-8 text-center text-sm font-semibold text-antique-wood">
                {toPersianNumbers(item.quantity)}
              </span>
              <button
                onClick={() => updateMutation.mutate({ itemId: item.id, quantity: item.quantity + 1 })}
                className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-antique-gold/10 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>

            <p className="w-24 text-left text-sm font-bold text-antique-wood">
              {formatPrice(item.product.price * item.quantity)}
            </p>

            <button
              onClick={() => removeMutation.mutate(item.id)}
              className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-red-100 hover:text-red-600 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>

      <div className="mt-6 card">
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-antique-wood">{t.cart.total}</span>
          <span className="text-2xl font-bold text-antique-gold">{formatPrice(cart?.total_price ?? 0)}</span>
        </div>
        <Button
          className="mt-4 w-full"
          onClick={() => checkoutMutation.mutate()}
          isLoading={checkoutMutation.isPending}
        >
          {t.cart.checkout}
        </Button>
      </div>
    </div>
  )
}
