import { useQuery } from '@tanstack/react-query'
import { Package, TrendingUp, Tag, DollarSign } from 'lucide-react'
import { adminApi } from '@/api/admin.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { CardSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice } from '@/utils/persian'

export function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => adminApi.getProducts({ page: 1, page_size: 100 }),
  })

  const stats = [
    {
      label: t.admin.totalProducts,
      value: toPersianNumbers(data?.total ?? 0),
      icon: Package,
      color: 'text-antique-gold bg-antique-gold/10',
    },
    {
      label: t.admin.activeProducts,
      value: toPersianNumbers(data?.items.filter((p) => p.is_active).length ?? 0),
      icon: TrendingUp,
      color: 'text-green-700 bg-green-100',
    },
    {
      label: t.admin.categories,
      value: toPersianNumbers(new Set(data?.items.map((p) => p.category)).size ?? 0),
      icon: Tag,
      color: 'text-antique-bronze bg-antique-bronze/10',
    },
    {
      label: t.admin.totalValue,
      value: formatPrice(data?.items.reduce((sum, p) => sum + p.price * p.quantity, 0) ?? 0),
      icon: DollarSign,
      color: 'text-antique-sepia bg-antique-sepia/10',
    },
  ]

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.admin.dashboardTitle}</h1>
        <p className="mt-1 text-sm text-antique-sepia/60">{t.admin.dashboardSubtitle}</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="card">
              <div className="flex items-center gap-4">
                <div className={`rounded-xl p-3 ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-sm font-medium text-antique-sepia/60">{stat.label}</p>
                  <p className="text-xl font-bold text-antique-wood">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
