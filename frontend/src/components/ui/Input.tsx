import { type InputHTMLAttributes, forwardRef, type ReactNode } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  endAdornment?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', endAdornment, ...props }, ref) => {
    return (
      <div className="space-y-1.5">
        {label && <label className="label">{label}</label>}
        <div className="relative">
          <input
            ref={ref}
            className={`input-field ${endAdornment ? 'pl-10' : ''} ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''} ${className}`}
            {...props}
          />
          {endAdornment && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2">
              {endAdornment}
            </div>
          )}
        </div>
        {error && <p className="text-xs text-red-600 font-medium">{error}</p>}
      </div>
    )
  }
)

Input.displayName = 'Input'
