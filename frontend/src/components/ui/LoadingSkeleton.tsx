interface LoadingSkeletonProps {
  rows?: number
  className?: string
}

export function LoadingSkeleton({ rows = 3, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-4 w-3/4 rounded bg-antique-gold/10" />
          <div className="mt-2 h-4 w-1/2 rounded bg-antique-gold/10" />
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="card space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 animate-pulse">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="h-4 flex-1 rounded bg-antique-gold/10" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-32 rounded-lg bg-antique-gold/10" />
      <div className="mt-4 space-y-2">
        <div className="h-4 w-3/4 rounded bg-antique-gold/10" />
        <div className="h-4 w-1/2 rounded bg-antique-gold/10" />
      </div>
    </div>
  )
}
