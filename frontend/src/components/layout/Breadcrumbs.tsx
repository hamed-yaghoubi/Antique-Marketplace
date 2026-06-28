import { Link, useLocation } from 'react-router-dom'
import { ChevronLeft, Home } from 'lucide-react'
import { t } from '@/utils/persian'

export function Breadcrumbs() {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter((x) => x)

  if (pathnames.length === 0) return null

  const breadcrumbMap: Record<string, string> = {
    products: t.nav.products,
    admin: t.nav.admin,
    dashboard: t.nav.dashboard,
    cart: t.nav.cart,
    orders: 'سفارشات',
    settings: 'تنظیمات',
  }

  return (
    <nav className="mb-6 flex items-center gap-1 text-sm text-antique-sepia-light">
      <Link to="/" className="hover:text-antique-gold transition-colors">
        <Home className="h-4 w-4" />
      </Link>
      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`
        const isLast = index === pathnames.length - 1
        const label = breadcrumbMap[name] || name

        return (
          <span key={routeTo} className="flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" />
            {isLast ? (
              <span className="font-semibold text-antique-wood">{label}</span>
            ) : (
              <Link to={routeTo} className="hover:text-antique-gold transition-colors">
                {label}
              </Link>
            )}
          </span>
        )
      })}
    </nav>
  )
}
