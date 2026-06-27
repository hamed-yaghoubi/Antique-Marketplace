import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Crown } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { t } from '@/utils/persian'

const loginSchema = z.object({
  username: z.string().min(1, t.validation.required),
  password: z.string().min(1, t.validation.required),
  remember_me: z.boolean().optional(),
})

type LoginForm = z.infer<typeof loginSchema>

export function Login() {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
      remember_me: false,
    },
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      await login(data.username, data.password)
      toast.success(t.auth.welcomeBack)
      navigate('/')
    } catch (error) {
      const message = error instanceof Error ? error.message : t.auth.loginFailed
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 parchment-bg vignette">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-antique-gold/20 border-2 border-antique-gold/30">
            <Crown className="h-8 w-8 text-antique-gold" />
          </div>
          <h1 className="text-3xl font-bold text-antique-wood text-shadow-vintage">{t.auth.loginTitle}</h1>
          <p className="mt-2 text-sm text-antique-sepia/70">{t.auth.loginSubtitle}</p>
        </div>

        <div className="card">
          <div className="mb-4 text-center">
            <span className="ornament">✦ ✦ ✦</span>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={t.auth.username}
              placeholder={t.auth.usernamePlaceholder}
              error={errors.username?.message}
              {...register('username')}
            />

            <Input
              label={t.auth.password}
              type="password"
              placeholder={t.auth.passwordPlaceholder}
              error={errors.password?.message}
              {...register('password')}
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-antique-gold/30 text-antique-gold focus:ring-antique-gold"
                  {...register('remember_me')}
                />
                <span className="text-sm text-antique-sepia/70">{t.auth.rememberMe}</span>
              </label>
            </div>

            <Button type="submit" isLoading={isLoading} className="w-full">
              {t.auth.signIn}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <span className="ornament text-sm">— ✦ —</span>
          </div>
        </div>
      </div>
    </div>
  )
}
