import { type ReactNode, useEffect } from 'react'
import { X } from 'lucide-react'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}

export function Modal({ isOpen, onClose, title, children, size = 'md' }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-antique-ink/50 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative ${sizeClasses[size]} w-full mx-4 rounded-xl border-2 border-antique-gold/30 bg-antique-cream shadow-vintage-lg`}>
        <div className="flex items-center justify-between border-b-2 border-antique-gold/20 px-6 py-4">
          <h2 className="text-lg font-bold text-antique-wood">{title}</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-antique-sepia-light hover:bg-antique-gold/10 hover:text-antique-wood transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-6 py-4">{children}</div>
      </div>
    </div>
  )
}
