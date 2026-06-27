import type { ReactNode } from 'react'

interface BadgeProps {
  children: ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}

const variantClasses = {
  default: 'bg-antique-gold/10 text-antique-wood border border-antique-gold/20',
  success: 'bg-green-100 text-green-800 border border-green-200',
  warning: 'bg-amber-100 text-amber-800 border border-amber-200',
  danger: 'bg-red-100 text-red-800 border border-red-200',
  info: 'bg-blue-100 text-blue-800 border border-blue-200',
}

export function Badge({ children, variant = 'default' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${variantClasses[variant]}`}>
      {children}
    </span>
  )
}
