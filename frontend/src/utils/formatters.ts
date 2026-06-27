import { toPersianNumbers, formatPrice, formatJalali, formatJalaliDateTime } from './persian'

export function formatCurrency(amount: number): string {
  return formatPrice(amount)
}

export function formatDate(dateString: string): string {
  return formatJalali(dateString)
}

export function formatDateTime(dateString: string): string {
  return formatJalaliDateTime(dateString)
}

export function toPersianDigits(str: string | number): string {
  return toPersianNumbers(str)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}
