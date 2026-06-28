import { Link } from 'react-router-dom'
import { LogOut, User, LogIn, UserPlus } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Badge } from '@/components/ui/Badge'
import { t } from '@/utils/persian'

export function Header() {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b-2 border-antique-gold/20 bg-antique-cream/80 px-6 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        {isAuthenticated ? (
          <>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-antique-gold/20">
              <User className="h-4 w-4 text-antique-gold" />
            </div>
            <Link to="/profile" className="text-sm font-semibold text-antique-wood hover:text-antique-gold transition-colors">
              {user?.username}
            </Link>
            {user?.role === 'admin' && (
              <Badge variant="info">مدیر</Badge>
            )}
          </>
        ) : (
          <span className="text-sm text-antique-sepia-light">{t.auth.loginSubtitle}</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {isAuthenticated ? (
          <button
            onClick={logout}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-antique-sepia-light transition-colors hover:bg-red-50 hover:text-red-700"
          >
            <LogOut className="h-4 w-4" />
            {t.auth.logout}
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-antique-sepia-light transition-colors hover:bg-antique-gold/10 hover:text-antique-gold"
            >
              <LogIn className="h-4 w-4" />
              {t.auth.signIn}
            </Link>
            <Link
              to="/register"
              className="flex items-center gap-2 rounded-lg bg-antique-gold px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-antique-gold-dark"
            >
              <UserPlus className="h-4 w-4" />
              {t.auth.signUp}
            </Link>
          </div>
        )}
      </div>
    </header>
  )
}
