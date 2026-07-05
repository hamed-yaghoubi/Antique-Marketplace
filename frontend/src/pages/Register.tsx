import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Crown, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { t } from '@/utils/persian'

const registerSchema = z.object({
  username: z.string().min(3, 'نام کاربری حداقل ۳ کاراکتر باشد'),
  password: z
    .string()
    .min(8, 'رمز عبور حداقل ۸ کاراکتر باشد')
    .regex(/[A-Z]/, 'رمز عبور باید حداقل شامل یک حرف بزرگ باشد')
    .regex(/[a-z]/, 'رمز عبور باید حداقل شامل یک حرف کوچک باشد')
    .regex(/[0-9]/, 'رمز عبور باید حداقل شامل یک عدد باشد'),
  confirm_password: z.string().min(1, t.validation.required),
}).refine((data) => data.password === data.confirm_password, {
  message: t.auth.passwordMismatch,
  path: ['confirm_password'],
})

type RegisterForm = z.infer<typeof registerSchema>

export function Register() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      password: '',
      confirm_password: '',
    },
  })

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true)
    try {
      await registerUser(data.username, data.password, data.confirm_password)
      toast.success(t.auth.registerSuccess)
      navigate('/')
    } catch (error) {
      const message = error instanceof Error ? error.message : t.auth.registerFailed
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
          <h1 className="text-3xl font-bold text-antique-wood text-shadow-vintage">{t.auth.registerTitle}</h1>
          <p className="mt-2 text-sm text-antique-sepia-light">{t.auth.registerSubtitle}</p>
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
              type={showPassword ? 'text' : 'password'}
              placeholder={t.auth.passwordPlaceholder}
              error={errors.password?.message}
              endAdornment={
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  className="text-antique-sepia-light hover:text-antique-gold transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
              {...register('password')}
            />

            <Input
              label={t.auth.confirmPassword}
              type={showConfirm ? 'text' : 'password'}
              placeholder={t.auth.passwordPlaceholder}
              error={errors.confirm_password?.message}
              endAdornment={
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowConfirm((v) => !v)}
                  className="text-antique-sepia-light hover:text-antique-gold transition-colors"
                >
                  {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
              {...register('confirm_password')}
            />

            <Button type="submit" isLoading={isLoading} className="w-full">
              {t.auth.signUp}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <span className="ornament text-sm">— ✦ —</span>
          </div>

          <p className="mt-4 text-center text-sm text-antique-sepia-light">
            {t.auth.hasAccount}{' '}
            <Link to="/login" className="font-semibold text-antique-gold hover:text-antique-gold-dark transition-colors">
              {t.auth.signIn}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
