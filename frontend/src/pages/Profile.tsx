import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { User, Lock } from 'lucide-react'
import { authApi } from '@/api/auth.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useAuth } from '@/contexts/AuthContext'
import { t, formatJalali } from '@/utils/persian'

const passwordSchema = z.object({
  current_password: z.string().min(1, t.validation.required),
  new_password: z.string().min(6, 'رمز عبور حداقل ۶ کاراکتر باشد'),
  confirm_password: z.string().min(1, t.validation.required),
}).refine((data) => data.new_password === data.confirm_password, {
  message: t.auth.passwordMismatch,
  path: ['confirm_password'],
})

type PasswordForm = z.infer<typeof passwordSchema>

export function Profile() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
  })

  const onSubmit = async (data: PasswordForm) => {
    setIsLoading(true)
    try {
      await authApi.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      })
      toast.success(t.profile.passwordChanged)
      reset()
    } catch (error) {
      const message = error instanceof Error ? error.message : t.profile.passwordChangeFailed
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <Breadcrumbs />
      <h1 className="mb-6 text-2xl font-bold text-antique-wood text-shadow-vintage">{t.profile.title}</h1>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-antique-gold/20">
              <User className="h-8 w-8 text-antique-gold" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-antique-wood">{user?.username}</h2>
              <div className="mt-1 flex items-center gap-2">
                <Badge variant={user?.role === 'admin' ? 'info' : 'default'}>
                  {user?.role === 'admin' ? 'مدیر' : 'کاربر'}
                </Badge>
              </div>
            </div>
          </div>
          <div className="mt-6 space-y-3 border-t border-antique-gold/20 pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-antique-sepia-light">{t.profile.memberSince}</span>
              <span className="text-sm font-semibold text-antique-wood">
                {user?.created_at ? formatJalali(user.created_at) : '-'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-antique-sepia-light">{t.auth.username}</span>
              <span className="text-sm font-semibold text-antique-wood">{user?.username}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="mb-4 flex items-center gap-3">
            <Lock className="h-5 w-5 text-antique-gold" />
            <h2 className="text-lg font-bold text-antique-wood">{t.profile.changePassword}</h2>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={t.profile.currentPassword}
              type="password"
              error={errors.current_password?.message}
              {...register('current_password')}
            />
            <Input
              label={t.profile.newPassword}
              type="password"
              error={errors.new_password?.message}
              {...register('new_password')}
            />
            <Input
              label={t.profile.confirmPassword}
              type="password"
              error={errors.confirm_password?.message}
              {...register('confirm_password')}
            />
            <Button type="submit" isLoading={isLoading}>
              {t.profile.updatePassword}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
