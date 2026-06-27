import { LogOut, Moon, Sun, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import { Badge } from '@/components/ui/Badge'
import { t } from '@/utils/persian'

export function Header() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b-2 border-antique-gold/20 bg-antique-cream/80 px-6 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-antique-gold/20">
          <User className="h-4 w-4 text-antique-gold" />
        </div>
        <span className="text-sm font-semibold text-antique-wood">
          {user?.username}
        </span>
        {user?.role === 'admin' && (
          <Badge variant="info">{t.auth.signIn === 'ورود' ? 'مدیر' : 'Admin'}</Badge>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-antique-sepia/60 hover:bg-antique-gold/10 hover:text-antique-gold transition-colors"
        >
          {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
        </button>
        <button
          onClick={logout}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-antique-sepia/70 transition-colors hover:bg-red-50 hover:text-red-700"
        >
          <LogOut className="h-4 w-4" />
          {t.auth.logout}
        </button>
      </div>
    </header>
  )
}
