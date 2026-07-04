import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Package, ShoppingCart, Crown, Shield, ListOrdered, User, Store, Users } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { t } from '@/utils/persian'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
    isActive
      ? 'bg-antique-gold/20 text-antique-gold shadow-sm'
      : 'text-antique-cream hover:bg-antique-gold/10 hover:text-antique-gold'
  }`

const publicItems = [
  { to: '/', icon: Package, label: t.nav.products, end: true },
]

const customerItems = [
  { to: '/customer/dashboard', icon: LayoutDashboard, label: t.nav.dashboard },
  { to: '/cart', icon: ShoppingCart, label: t.nav.cart },
  { to: '/orders', icon: ListOrdered, label: t.nav.myOrders },
]

const sellerItems = [
  { to: '/my-products', icon: Store, label: t.nav.myProducts },
  { to: '/seller/orders', icon: ListOrdered, label: t.nav.sellerOrders },
]

const adminItems = [
  { to: '/admin', icon: LayoutDashboard, label: t.nav.dashboard },
  { to: '/admin/products', icon: Shield, label: t.nav.manageProducts },
  { to: '/admin/orders', icon: ListOrdered, label: t.nav.adminOrders },
  { to: '/admin/users', icon: Users, label: t.nav.manageUsers },
]

export function Sidebar() {
  const { isAuthenticated, isAdmin, isOwner } = useAuth()

  return (
    <aside className="fixed right-0 top-0 z-40 h-screen w-64 sidebar-style">
      <div className="flex h-16 items-center gap-3 border-b border-antique-gold/20 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-antique-gold/20">
          <Crown className="h-5 w-5 text-antique-gold" />
        </div>
        <div>
          <span className="text-lg font-bold text-antique-gold">{t.layout.marketplace}</span>
          <span className="block text-[10px] text-antique-gold/60 tracking-wider">ANTIQUE</span>
        </div>
      </div>

      <nav className="space-y-1 px-3 py-4">
        <div className="mb-3 px-3 text-xs font-semibold text-antique-gold/50">
          {t.layout.marketplace}
        </div>
        {publicItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={navLinkClass}
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}

        {isAuthenticated && (
          <>
            <div className="mb-3 mt-6 px-3 text-xs font-semibold text-antique-gold/50">
              {t.nav.customer}
            </div>
            {customerItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={navLinkClass}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </NavLink>
            ))}

            {!isAdmin && (
              <>
                <div className="mb-3 mt-6 px-3 text-xs font-semibold text-antique-gold/50">
                  {t.nav.seller}
                </div>
                {sellerItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={navLinkClass}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                ))}
              </>
            )}

            {isAdmin && (
              <>
                <div className="mb-3 mt-6 px-3 text-xs font-semibold text-antique-gold/50">
                  {t.nav.seller}
                </div>
                {sellerItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={navLinkClass}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                ))}

                <div className="mb-3 mt-6 px-3 text-xs font-semibold text-antique-gold/50">
                  {t.layout.admin}
                </div>
                {adminItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/admin'}
                    className={navLinkClass}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                ))}
              </>
            )}

            <NavLink
              to="/profile"
              className={navLinkClass}
            >
              <User className="h-5 w-5" />
              {t.nav.profile}
            </NavLink>
          </>
        )}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 border-t border-antique-gold/10 px-6 py-4">
        <div className="ornament text-center text-lg">✦</div>
      </div>
    </aside>
  )
}
