import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight, ShoppingCart } from 'lucide-react'
import toast from 'react-hot-toast'
import { productsApi } from '@/api/products.api'
import { cartApi } from '@/api/cart.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { CardSkeleton } from '@/components/ui/LoadingSkeleton'
import { useAuth } from '@/contexts/AuthContext'
import { t, toPersianNumbers, formatPrice } from '@/utils/persian'
import type { ProductFilters, ProductCategory } from '@/types/products'

const categories: Array<{ value: ProductCategory; label: string }> = [
  { value: 'coin', label: 'سکه' },
  { value: 'clock', label: 'ساعت' },
  { value: 'painting', label: 'نقاشی' },
  { value: 'book', label: 'کتاب' },
  { value: 'statue', label: ' مجسمه' },
]

const sortOptions = [
  { value: 'created_at', label: t.products.dateCreated },
  { value: 'price', label: t.products.price },
  { value: 'title', label: t.products.name },
]

export function Products() {
  const [filters, setFilters] = useState<ProductFilters>({
    page: 1,
    page_size: 12,
    sort_by: 'created_at',
    sort_order: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['products', filters],
    queryFn: () => productsApi.getProducts(filters),
  })

  const addToCartMutation = useMutation({
    mutationFn: (productId: number) => cartApi.addItem({ product_id: productId, quantity: 1 }),
    onSuccess: () => {
      toast.success(t.cart.itemAdded)
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
    onError: (error: Error) => {
      toast.error(error.message || t.cart.addToCartFailed)
    },
  })

  const updateFilter = (key: keyof ProductFilters, value: string | number | boolean | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.products.title}</h1>
          <p className="mt-1 text-sm text-antique-sepia-light">{t.products.subtitle}</p>
        </div>
        <Button variant="secondary" onClick={() => setShowFilters(!showFilters)}>
          <SlidersHorizontal className="h-4 w-4" />
          {t.products.filters}
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia" />
            <input
              type="text"
              placeholder={t.products.search}
              className="input-field pr-10"
              value={filters.search || ''}
              onChange={(e) => updateFilter('search', e.target.value || undefined)}
            />
          </div>
        </div>
        <Select
          options={sortOptions}
          value={filters.sort_by}
          onChange={(e) => updateFilter('sort_by', e.target.value)}
          className="w-auto"
        />
        <Select
          options={[
            { value: 'desc', label: t.products.descending },
            { value: 'asc', label: t.products.ascending },
          ]}
          value={filters.sort_order}
          onChange={(e) => updateFilter('sort_order', e.target.value as 'asc' | 'desc')}
          className="w-auto"
        />
      </div>

      {showFilters && (
        <div className="mb-6 card">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Select
              label={t.products.category}
              options={categories}
              placeholder={t.products.allCategories}
              value={filters.category || ''}
              onChange={(e) => updateFilter('category', e.target.value || undefined)}
            />
            <div className="space-y-1.5">
              <label className="label">{t.products.minPrice}</label>
              <input
                type="number"
                placeholder="۰"
                className="input-field"
                value={filters.min_price || ''}
                onChange={(e) => updateFilter('min_price', e.target.value ? Number(e.target.value) : undefined)}
              />
            </div>
            <div className="space-y-1.5">
              <label className="label">{t.products.maxPrice}</label>
              <input
                type="number"
                placeholder="۹۹۹۹"
                className="input-field"
                value={filters.max_price || ''}
                onChange={(e) => updateFilter('max_price', e.target.value ? Number(e.target.value) : undefined)}
              />
            </div>
            <Select
              label={t.products.status}
              options={[
                { value: 'true', label: t.products.active },
                { value: 'false', label: t.products.inactive },
              ]}
              placeholder={t.products.all}
              value={filters.is_active?.toString() || ''}
              onChange={(e) => updateFilter('is_active', e.target.value ? e.target.value === 'true' : undefined)}
            />
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="card py-16 text-center">
          <p className="text-lg font-semibold text-antique-wood">{t.products.noProducts}</p>
          <p className="mt-2 text-sm text-antique-sepia-light">{t.products.subtitle}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data?.items.map((product) => (
            <div key={product.id} className="card group overflow-hidden p-0 transition-all hover:shadow-vintage-lg">
              <div className="relative aspect-square overflow-hidden bg-antique-gold/5">
                {product.main_image ? (
                  <img
                    src={product.main_image.image_url}
                    alt={product.title}
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center">
                    <span className="text-sm text-antique-sepia">{t.products.noImage}</span>
                  </div>
                )}
                <div className="absolute left-3 top-3">
                  <Badge variant="info">{categories.find(c => c.value === product.category)?.label ?? product.category}</Badge>
                </div>
              </div>
              <div className="p-4">
                <Link to={`/products/${product.id}`}>
                  <h3 className="font-bold text-antique-wood hover:text-antique-gold transition-colors line-clamp-1">
                    {product.title}
                  </h3>
                </Link>
                <p className="mt-1 text-lg font-bold text-antique-gold">{formatPrice(product.price)}</p>
                <div className="mt-3 flex items-center gap-2">
                  <Link to={`/products/${product.id}`} className="flex-1">
                    <Button variant="secondary" size="sm" className="w-full">
                      {t.products.viewDetails}
                    </Button>
                  </Link>
                  {isAuthenticated && (
                    <Button
                      size="sm"
                      onClick={() => addToCartMutation.mutate(product.id)}
                      isLoading={addToCartMutation.isPending}
                    >
                      <ShoppingCart className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {data && data.total_pages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-antique-sepia-light">
            {t.products.showing} {toPersianNumbers(((data.page - 1) * data.page_size) + 1)} {t.products.to} {toPersianNumbers(Math.min(data.page * data.page_size, data.total))} {t.products.from} {toPersianNumbers(data.total)} {t.products.results}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={data.page >= data.total_pages}
              onClick={() => updateFilter('page', data.page + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <span className="text-sm font-semibold text-antique-wood">
              {t.products.page} {toPersianNumbers(data.page)} {t.products.of} {toPersianNumbers(data.total_pages)}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={data.page <= 1}
              onClick={() => updateFilter('page', data.page - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
