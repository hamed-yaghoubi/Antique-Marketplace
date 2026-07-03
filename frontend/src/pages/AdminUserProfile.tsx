import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, User } from 'lucide-react'
import { adminApi } from '@/api/admin.api'
import { productsApi } from '@/api/products.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, formatJalali, formatPrice } from '@/utils/persian'
import type { ProductCategory } from '@/types/products'

const categories: Array<{ value: ProductCategory; label: string }> = [
  { value: 'coin', label: 'سکه' },
  { value: 'clock', label: 'ساعت' },
  { value: 'painting', label: 'نقاشی' },
  { value: 'book', label: 'کتاب' },
  { value: 'statue', label: ' مجسمه' },
]

export function AdminUserProfile() {
  const { id } = useParams<{ id: string }>()

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['admin-user', id],
    queryFn: () => adminApi.getUser(Number(id)),
    enabled: !!id,
  })

  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['admin-user-products', id],
    queryFn: () => productsApi.getProducts({ seller_id: Number(id), page: 1, page_size: 100 }),
    enabled: !!id,
  })

  if (userLoading || productsLoading) {
    return (
      <div>
        <Breadcrumbs />
        <LoadingSkeleton rows={4} />
      </div>
    )
  }

  if (!user) {
    return (
      <div>
        <Breadcrumbs />
        <div className="card py-16 text-center">
          <p className="text-lg font-semibold text-antique-wood">{t.admin.noUsers}</p>
          <Link to="/admin/users" className="mt-4 inline-block">
            <Button variant="secondary">{t.admin.manageUsers}</Button>
          </Link>
        </div>
      </div>
    )
  }

  const products = productsData?.items || []

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-4">
        <Link to="/admin/users" className="inline-flex items-center gap-2 text-sm text-antique-sepia-light hover:text-antique-gold transition-colors">
          <ArrowRight className="h-4 w-4" />
          {t.admin.manageUsers}
        </Link>
      </div>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{user.username}</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-antique-gold/20">
              <User className="h-8 w-8 text-antique-gold" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-antique-wood">{user.username}</h2>
              <div className="mt-1 flex items-center gap-2">
                <Badge variant={user.role === 'owner' ? 'warning' : user.role === 'admin' ? 'info' : 'default'}>
                  {user.role === 'owner' ? t.admin.ownerRole : user.role === 'admin' ? t.admin.adminRole : t.admin.userRole}
                </Badge>
                <Badge variant={user.is_active ? 'success' : 'danger'}>
                  {user.is_active ? t.admin.active : t.admin.banned}
                </Badge>
              </div>
            </div>
          </div>
          <div className="mt-6 space-y-3 border-t border-antique-gold/20 pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-antique-sepia-light">{t.profile.memberSince}</span>
              <span className="text-sm font-semibold text-antique-wood">
                {user.created_at ? formatJalali(user.created_at) : '-'}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="mb-4 text-lg font-bold text-antique-wood">{t.products.myProducts}</h2>
          {products.length === 0 ? (
            <p className="text-sm text-antique-sepia-light">{t.products.noProducts}</p>
          ) : (
            <div className="space-y-3">
              {products.map((product) => (
                <Link key={product.id} to={`/products/${product.id}`} className="flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-antique-gold/5">
                  {product.main_image ? (
                    <img src={product.main_image.image_url} alt={product.title} className="h-10 w-10 rounded-lg object-cover border border-antique-gold/20" />
                  ) : (
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-antique-gold/10 border border-antique-gold/20">
                      <span className="text-[10px] text-antique-sepia">{t.products.noImage}</span>
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-antique-wood line-clamp-1">{product.title}</p>
                    <p className="text-xs text-antique-sepia-light">
                      {categories.find(c => c.value === product.category)?.label ?? product.category}
                    </p>
                  </div>
                  <p className="text-sm font-bold text-antique-gold">{formatPrice(product.price)}</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
