import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ShoppingCart } from 'lucide-react'
import toast from 'react-hot-toast'
import { productsApi } from '@/api/products.api'
import { cartApi } from '@/api/cart.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useAuth } from '@/contexts/AuthContext'
import { t, toPersianNumbers, formatPrice, formatJalali } from '@/utils/persian'
import { queryKeys, invalidateCart } from '@/lib/queryKeys'
import type { ProductCategory } from '@/types/products'

const categories: Array<{ value: ProductCategory; label: string }> = [
  { value: 'coin', label: 'سکه' },
  { value: 'clock', label: 'ساعت' },
  { value: 'painting', label: 'نقاشی' },
  { value: 'book', label: 'کتاب' },
  { value: 'statue', label: 'مجسمه' },
]

export function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  const { data: product, isLoading, error } = useQuery({
    queryKey: queryKeys.products.detail(Number(id)),
    queryFn: () => productsApi.getProduct(Number(id)),
    enabled: !!id,
  })

  useEffect(() => {
    if (product?.images?.length && !selectedImage) {
      setSelectedImage(product.images[0]?.image_url ?? null)
    }
  }, [product, selectedImage])

  const addToCartMutation = useMutation({
    mutationFn: (productId: number) => cartApi.addItem({ product_id: productId, quantity: 1 }),
    onSuccess: () => {
      toast.success(t.cart.itemAdded)
      invalidateCart(queryClient)
    },
    onError: (error: Error) => {
      toast.error(error.message || t.cart.addToCartFailed)
    },
  })

  if (isLoading) {
    return (
      <div>
        <Breadcrumbs />
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="card animate-pulse">
            <div className="aspect-square rounded-lg bg-antique-gold/10" />
          </div>
          <div className="card space-y-4 animate-pulse">
            <div className="h-8 w-3/4 rounded bg-antique-gold/10" />
            <div className="h-6 w-1/2 rounded bg-antique-gold/10" />
            <div className="h-4 w-full rounded bg-antique-gold/10" />
            <div className="h-4 w-full rounded bg-antique-gold/10" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div>
        <Breadcrumbs />
        <div className="card py-16 text-center">
          <p className="text-lg font-semibold text-antique-wood">{t.products.noProducts}</p>
          <Link to="/" className="mt-4 inline-block">
            <Button variant="secondary">{t.products.backToProducts}</Button>
          </Link>
        </div>
      </div>
    )
  }

  const images = product.images || []
  const mainImage = selectedImage || product.main_image?.image_url

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-4">
        <Link to="/" className="inline-flex items-center gap-2 text-sm text-antique-sepia-light hover:text-antique-gold transition-colors">
          <ArrowRight className="h-4 w-4" />
          {t.products.backToProducts}
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="card overflow-hidden p-0">
            {mainImage ? (
              <img
                src={mainImage}
                alt={product.title}
                className={`aspect-square w-full object-cover ${product.quantity <= 0 ? 'grayscale' : ''}`}
              />
            ) : (
              <div className="flex aspect-square w-full items-center justify-center bg-antique-gold/5">
                <span className="text-antique-sepia">{t.products.noImage}</span>
              </div>
            )}
          </div>
          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {images.map((image) => (
                <button
                  key={image.id}
                  onClick={() => setSelectedImage(image.image_url)}
                  className={`h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg border-2 transition-colors ${
                    selectedImage === image.image_url
                      ? 'border-antique-gold'
                      : 'border-antique-gold/20 hover:border-antique-gold/50'
                  }`}
                >
                  <img src={image.image_url} alt="" className="h-full w-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div>
            <Badge variant="info">
              {categories.find(c => c.value === product.category)?.label ?? product.category}
            </Badge>
            <h1 className="mt-3 text-3xl font-bold text-antique-wood text-shadow-vintage">
              {product.title}
            </h1>
            <p className="mt-2 text-3xl font-bold text-antique-gold">
              {formatPrice(product.price)}
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 ${product.quantity > 0 ? 'text-green-700' : 'text-red-700'}`}>
              <div className={`h-3 w-3 rounded-full ${product.quantity > 0 ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm font-medium">
                {product.quantity > 0
                  ? `${t.products.inStock} (${toPersianNumbers(product.quantity)} ${t.products.stock})`
                  : t.products.outOfStock
                }
              </span>
            </div>
          </div>

          {product.description && (
            <div>
              <h3 className="mb-2 text-sm font-bold text-antique-wood">{t.products.description}</h3>
              <p className="text-sm leading-relaxed text-antique-sepia-light">{product.description}</p>
            </div>
          )}

          <div className="rounded-lg bg-antique-gold/5 p-4 border border-antique-gold/20">
            <p className="text-xs text-antique-sepia-light">
              {t.products.dateCreated}: {formatJalali(product.created_at)}
            </p>
          </div>

          <div className="flex gap-3">
            {isAuthenticated ? (
              <Button
                className="flex-1"
                onClick={() => addToCartMutation.mutate(product.id)}
                isLoading={addToCartMutation.isPending}
                disabled={product.quantity <= 0}
              >
                <ShoppingCart className="h-5 w-5" />
                {t.products.addToCart}
              </Button>
            ) : (
              <Link to="/login" className="flex-1">
                <Button className="w-full">
                  {t.auth.signIn}
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
