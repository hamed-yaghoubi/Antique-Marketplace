import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react'
import { productsApi } from '@/api/products.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
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
    page_size: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['products', filters],
    queryFn: () => productsApi.getProducts(filters),
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
          <p className="mt-1 text-sm text-antique-sepia/60">{t.products.subtitle}</p>
        </div>
        <Button variant="secondary" onClick={() => setShowFilters(!showFilters)}>
          <SlidersHorizontal className="h-4 w-4" />
          {t.products.filters}
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia/40" />
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
            <Input
              label={t.products.minPrice}
              type="number"
              placeholder="۰"
              value={filters.min_price || ''}
              onChange={(e) => updateFilter('min_price', e.target.value ? Number(e.target.value) : undefined)}
            />
            <Input
              label={t.products.maxPrice}
              type="number"
              placeholder="۹۹۹۹"
              value={filters.max_price || ''}
              onChange={(e) => updateFilter('max_price', e.target.value ? Number(e.target.value) : undefined)}
            />
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
            <Input
              label={t.products.minStock}
              type="number"
              placeholder="۰"
              value={filters.min_quantity || ''}
              onChange={(e) => updateFilter('min_quantity', e.target.value ? Number(e.target.value) : undefined)}
            />
            <Input
              label={t.products.maxStock}
              type="number"
              placeholder="۹۹۹"
              value={filters.max_quantity || ''}
              onChange={(e) => updateFilter('max_quantity', e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={5} cols={5} />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-antique-gold/20 bg-antique-gold/5">
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.product}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.sku}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.categoryLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.priceLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.statusLabel}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-antique-gold/10">
              {data?.items.map((product) => (
                <tr key={product.id} className="transition-colors hover:bg-antique-gold/5">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {product.main_image ? (
                        <img src={product.main_image.image_url} alt={product.title} className="h-10 w-10 rounded-lg object-cover border border-antique-gold/20" />
                      ) : (
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-antique-gold/10 border border-antique-gold/20">
                          <span className="text-[10px] text-antique-sepia/50">{t.products.noImage}</span>
                        </div>
                      )}
                      <span className="font-semibold text-antique-wood">{product.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-antique-sepia/70">{toPersianNumbers(product.sku)}</td>
                  <td className="px-6 py-4">
                    <Badge variant="info">{categories.find(c => c.value === product.category)?.label ?? product.category}</Badge>
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-antique-wood">{formatPrice(product.price)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={product.is_active ? 'success' : 'warning'}>
                      {product.is_active ? t.products.active : t.products.inactive}
                    </Badge>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-sm text-antique-sepia/50">
                    {t.products.noProducts}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total_pages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-antique-sepia/60">
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
