import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { t } from '@/utils/persian'

export function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 parchment-bg vignette">
      <div className="text-center">
        <h1 className="text-7xl font-bold text-antique-gold text-shadow-vintage">{t.notFound.title}</h1>
        <p className="mt-4 text-xl font-semibold text-antique-wood">{t.notFound.message}</p>
        <p className="mt-2 text-sm text-antique-sepia/60">
          {t.notFound.description}
        </p>
        <div className="mt-6">
          <span className="ornament text-lg">✦ ✦ ✦</span>
        </div>
        <Link to="/" className="mt-6 inline-block">
          <Button>
            <Home className="h-4 w-4" />
            {t.notFound.backToHome}
          </Button>
        </Link>
      </div>
    </div>
  )
}
