import { z } from 'zod'
import { t } from './persian'

export const loginSchema = z.object({
  username: z.string().min(1, t.validation.required),
  password: z.string().min(1, t.validation.required),
})

export const productSchema = z.object({
  title: z.string().min(1, t.validation.required).max(255),
  description: z.string().min(1, t.validation.required),
  sku: z.string().min(1, t.validation.required).max(100),
  price: z.number().min(0, t.validation.positivePrice),
  quantity: z.number().int().min(0, t.validation.positiveQuantity),
  category: z.enum(['coin', 'clock', 'painting', 'book', 'statue']),
})

export const changePasswordSchema = z.object({
  current_password: z.string().min(1, t.validation.required),
  new_password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
  confirm_password: z.string().min(1, t.validation.required),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'رمزهای عبور مطابقت ندارند',
  path: ['confirm_password'],
})
