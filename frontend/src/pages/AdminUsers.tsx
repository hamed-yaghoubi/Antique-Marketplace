import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Shield, ShieldOff, ChevronDown, UserCheck } from 'lucide-react'
import { adminApi } from '@/api/admin.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, formatJalali } from '@/utils/persian'
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import type { User } from '@/types/auth'

export function AdminUsers() {
  const { user: currentUser, isOwner } = useAuth()
  const queryClient = useQueryClient()
  const [banTarget, setBanTarget] = useState<User | null>(null)
  const [unbanTarget, setUnbanTarget] = useState<User | null>(null)
  const [promoteTarget, setPromoteTarget] = useState<User | null>(null)

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: adminApi.getUsers,
  })

  const roleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: number; role: 'user' | 'admin' }) =>
      adminApi.updateUserRole(userId, role),
    onSuccess: () => {
      toast.success(t.admin.userRoleUpdated)
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error(t.admin.roleUpdateFailed),
  })

  const banMutation = useMutation({
    mutationFn: (userId: number) => adminApi.banUser(userId),
    onSuccess: () => {
      toast.success(t.admin.userBanned)
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setBanTarget(null)
    },
    onError: () => toast.error(t.admin.banFailed),
  })

  const unbanMutation = useMutation({
    mutationFn: (userId: number) => adminApi.unbanUser(userId),
    onSuccess: () => {
      toast.success(t.admin.userUnbanned)
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setUnbanTarget(null)
    },
    onError: () => toast.error(t.admin.unbanFailed),
  })

  const promoteMutation = useMutation({
    mutationFn: (userId: number) => adminApi.promoteUser(userId),
    onSuccess: () => {
      toast.success(t.admin.userPromoted)
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setPromoteTarget(null)
    },
    onError: () => toast.error(t.admin.promoteFailed),
  })

  const canTargetUser = (target: User) => {
    if (isOwner) return true
    if (currentUser?.id === target.id) return false
    return target.role === 'user'
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'owner':
        return <Badge variant="warning">{t.admin.ownerRole}</Badge>
      case 'admin':
        return <Badge variant="info">{t.admin.adminRole}</Badge>
      default:
        return <Badge variant="default">{t.admin.userRole}</Badge>
    }
  }

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.admin.manageUsers}</h1>
        <p className="mt-1 text-sm text-antique-sepia-light">{t.admin.manageUsersSubtitle}</p>
      </div>

      {isLoading ? (
        <TableSkeleton rows={5} cols={5} />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-antique-gold/20 bg-antique-gold/5">
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.user}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.role}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.status}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.joinDate}</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-antique-wood">{t.admin.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-antique-gold/10">
              {users?.map((user) => (
                <tr key={user.id} className="transition-colors hover:bg-antique-gold/5">
                  <td className="px-6 py-4">
                    <span className="font-semibold text-antique-wood">{user.username}</span>
                  </td>
                  <td className="px-6 py-4">
                    {getRoleBadge(user.role)}
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={user.is_active ? 'success' : 'danger'}>
                      {user.is_active ? t.admin.active : t.admin.banned}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-antique-sepia-light">
                    {formatJalali(user.created_at)}
                  </td>
                  <td className="px-6 py-4">
                    {canTargetUser(user) ? (
                      <div className="flex items-center gap-2">
                        {isOwner && user.role === 'user' && (
                          <button
                            onClick={() => setPromoteTarget(user)}
                            className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-green-100 hover:text-green-600 transition-colors"
                            title={t.admin.promote}
                          >
                            <UserCheck className="h-4 w-4" />
                          </button>
                        )}
                        {user.role !== 'owner' && (
                          <>
                            <div className="relative">
                              <select
                                value={user.role}
                                onChange={(e) => roleMutation.mutate({ userId: user.id, role: e.target.value as 'user' | 'admin' })}
                                disabled={roleMutation.isPending}
                                className="appearance-none rounded-lg border border-antique-gold/20 bg-white py-1.5 pl-8 pr-3 text-sm text-antique-wood focus:border-antique-gold focus:outline-none focus:ring-1 focus:ring-antique-gold disabled:opacity-50"
                              >
                                <option value="user">{t.admin.userRole}</option>
                                <option value="admin">{t.admin.adminRole}</option>
                              </select>
                              <ChevronDown className="pointer-events-none absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia" />
                            </div>
                            {user.is_active ? (
                              <button
                                onClick={() => setBanTarget(user)}
                                className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-red-100 hover:text-red-600 transition-colors"
                                title={t.admin.ban}
                              >
                                <ShieldOff className="h-4 w-4" />
                              </button>
                            ) : (
                              <button
                                onClick={() => setUnbanTarget(user)}
                                className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-green-100 hover:text-green-600 transition-colors"
                                title={t.admin.unban}
                              >
                                <Shield className="h-4 w-4" />
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-antique-sepia-light">—</span>
                    )}
                  </td>
                </tr>
              ))}
              {users?.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-sm text-antique-sepia-light">
                    {t.admin.noUsers}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={banTarget !== null} onClose={() => setBanTarget(null)} title={t.admin.ban} size="sm">
        <p className="text-sm text-antique-sepia-light">{t.admin.confirmBan}</p>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setBanTarget(null)}>{t.admin.cancel}</Button>
          <Button variant="danger" isLoading={banMutation.isPending} onClick={() => banTarget && banMutation.mutate(banTarget.id)}>
            {t.admin.ban}
          </Button>
        </div>
      </Modal>

      <Modal isOpen={unbanTarget !== null} onClose={() => setUnbanTarget(null)} title={t.admin.unban} size="sm">
        <p className="text-sm text-antique-sepia-light">{t.admin.confirmUnban}</p>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setUnbanTarget(null)}>{t.admin.cancel}</Button>
          <Button variant="primary" isLoading={unbanMutation.isPending} onClick={() => unbanTarget && unbanMutation.mutate(unbanTarget.id)}>
            {t.admin.unban}
          </Button>
        </div>
      </Modal>

      <Modal isOpen={promoteTarget !== null} onClose={() => setPromoteTarget(null)} title={t.admin.promote} size="sm">
        <p className="text-sm text-antique-sepia-light">{t.admin.confirmPromote}</p>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setPromoteTarget(null)}>{t.admin.cancel}</Button>
          <Button variant="primary" isLoading={promoteMutation.isPending} onClick={() => promoteTarget && promoteMutation.mutate(promoteTarget.id)}>
            {t.admin.promote}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
