import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Plus, Pencil, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react'
import { adminApi } from '@/api/admin.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice } from '@/utils/persian'
import type { Product, ProductFilters, ProductCategory, AdminProductCreate, AdminProductUpdate } from '@/types/products'

const categories: Array<{ value: ProductCategory; label: string }> = [
  { value: 'coin', label: 'سکه' },
  { value: 'clock', label: 'ساعت' },
  { value: 'painting', label: 'نقاشی' },
  { value: 'book', label: 'کتاب' },
  { value: 'statue', label: ' مجسمه' },
]

const productSchema = z.object({
  title: z.string().min(1, t.validation.required),
  description: z.string().min(1, t.validation.required),
  sku: z.string().min(1, t.validation.required),
  price: z.number().min(0, t.validation.positivePrice),
  quantity: z.number().min(0, t.validation.positiveQuantity),
  category: z.string().min(1, t.validation.required),
  seller_id: z.number().min(1, t.validation.required),
  is_active: z.boolean(),
})

type ProductForm = z.infer<typeof productSchema>

export function AdminProducts() {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState<ProductFilters>({ page: 1, page_size: 10, sort_by: 'created_at', sort_order: 'desc' })
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-products', filters],
    queryFn: () => adminApi.getProducts(filters),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProductForm>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      title: '',
      description: '',
      sku: '',
      price: 0,
      quantity: 0,
      category: '',
      seller_id: 1,
      is_active: true,
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: AdminProductCreate) => adminApi.createProduct(data),
    onSuccess: () => {
      toast.success(t.admin.productCreated)
      queryClient.invalidateQueries({ queryKey: ['admin-products'] })
      closeModal()
    },
    onError: () => toast.error(t.admin.createFailed),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AdminProductUpdate }) => adminApi.updateProduct(id, data),
    onSuccess: () => {
      toast.success(t.admin.productUpdated)
      queryClient.invalidateQueries({ queryKey: ['admin-products'] })
      closeModal()
    },
    onError: () => toast.error(t.admin.updateFailed),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => adminApi.deleteProduct(id),
    onSuccess: () => {
      toast.success(t.admin.productDeleted)
      queryClient.invalidateQueries({ queryKey: ['admin-products'] })
      setDeleteId(null)
    },
    onError: () => toast.error(t.admin.deleteFailed),
  })

  const openCreateModal = () => {
    setEditingProduct(null)
    reset({ title: '', description: '', sku: '', price: 0, quantity: 0, category: '', seller_id: 1, is_active: true })
    setIsModalOpen(true)
  }

  const openEditModal = (product: Product) => {
    setEditingProduct(product)
    reset({
      title: product.title,
      description: product.description,
      sku: product.sku,
      price: product.price,
      quantity: product.quantity,
      category: product.category,
      seller_id: product.seller_id,
      is_active: product.is_active,
    })
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingProduct(null)
    reset()
  }

  const onSubmit = (formData: ProductForm) => {
    if (editingProduct) {
      updateMutation.mutate({ id: editingProduct.id, data: formData })
    } else {
      createMutation.mutate(formData as AdminProductCreate)
    }
  }

  const updateFilter = (key: keyof ProductFilters, value: string | number | boolean | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  return (
    <div>
      <Breadcrumbs />
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-antique-wood text-shadow-vintage">{t.admin.manageTitle}</h1>
          <p className="mt-1 text-sm text-antique-sepia/60">{t.admin.manageSubtitle}</p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="h-4 w-4" />
          {t.admin.addProduct}
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia/40" />
            <input
              type="text"
              placeholder={t.products.search}
              className="input-field pr-10"
              value={filters.search || ''}
              onChange={(e) => updateFilter('search', e.target.value || undefined)}
            />
          </div>
        </div>
        <Select
          options={categories}
          placeholder={t.products.allCategories}
          value={filters.category || ''}
          onChange={(e) => updateFilter('category', e.target.value || undefined)}
          className="w-auto"
        />
        <Select
          options={[
            { value: 'true', label: t.products.active },
            { value: 'false', label: t.products.inactive },
          ]}
          placeholder={t.products.all}
          value={filters.is_active?.toString() || ''}
          onChange={(e) => updateFilter('is_active', e.target.value ? e.target.value === 'true' : undefined)}
          className="w-auto"
        />
      </div>

      {isLoading ? (
        <TableSkeleton rows={5} cols={6} />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-antique-gold/20 bg-antique-gold/5">
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.product}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.sku}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.categoryLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.priceLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.stock}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.statusLabel}</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-antique-wood">{t.admin.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-antique-gold/10">
              {data?.items.map((product) => (
                <tr key={product.id} className="transition-colors hover:bg-antique-gold/5">
                  <td className="px-6 py-4 font-semibold text-antique-wood">{product.title}</td>
                  <td className="px-6 py-4 text-sm text-antique-sepia/70">{toPersianNumbers(product.sku)}</td>
                  <td className="px-6 py-4"><Badge variant="info">{categories.find(c => c.value === product.category)?.label ?? product.category}</Badge></td>
                  <td className="px-6 py-4 text-sm font-bold text-antique-wood">{formatPrice(product.price)}</td>
                  <td className="px-6 py-4 text-sm text-antique-sepia/70">{toPersianNumbers(product.quantity)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={product.is_active ? 'success' : 'warning'}>
                      {product.is_active ? t.products.active : t.products.inactive}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button onClick={() => openEditModal(product)} className="rounded-lg p-1.5 text-antique-sepia/50 hover:bg-antique-gold/10 hover:text-antique-gold transition-colors">
                        <Pencil className="h-4 w-4" />
                      </button>
                      <button onClick={() => setDeleteId(product.id)} className="rounded-lg p-1.5 text-antique-sepia/50 hover:bg-red-100 hover:text-red-600 transition-colors">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-sm text-antique-sepia/50">
                    {t.products.noProducts}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total_pages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-antique-sepia/60">
            {t.products.page} {toPersianNumbers(data.page)} {t.products.of} {toPersianNumbers(data.total_pages)} ({toPersianNumbers(data.total)} مورد)
          </p>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" disabled={data.page >= data.total_pages} onClick={() => updateFilter('page', data.page + 1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button variant="secondary" size="sm" disabled={data.page <= 1} onClick={() => updateFilter('page', data.page - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingProduct ? t.admin.editProduct : t.admin.createProduct}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label={t.admin.title} placeholder={t.admin.titlePlaceholder} error={errors.title?.message} {...register('title')} />
          <Input label={t.admin.description} placeholder={t.admin.descriptionPlaceholder} error={errors.description?.message} {...register('description')} />
          <Input label={t.admin.skuLabel} placeholder={t.admin.skuPlaceholder} error={errors.sku?.message} {...register('sku')} />
          <div className="grid grid-cols-2 gap-4">
            <Input label={t.admin.priceLabel} type="number" step="0.01" error={errors.price?.message} {...register('price', { valueAsNumber: true })} />
            <Input label={t.admin.quantity} type="number" error={errors.quantity?.message} {...register('quantity', { valueAsNumber: true })} />
          </div>
          <Select label={t.admin.categoryLabel} options={categories} error={errors.category?.message} {...register('category')} />
          {!editingProduct && (
            <Input label={t.admin.sellerId} type="number" error={errors.seller_id?.message} {...register('seller_id', { valueAsNumber: true })} />
          )}
          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_active" className="h-4 w-4 rounded border-antique-gold/30 text-antique-gold" {...register('is_active')} />
            <label htmlFor="is_active" className="text-sm font-medium text-antique-wood">{t.admin.activeLabel}</label>
          </div>
          <div className="flex justify-start gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={closeModal}>{t.admin.cancel}</Button>
            <Button type="submit" isLoading={createMutation.isPending || updateMutation.isPending}>
              {editingProduct ? t.admin.update : t.admin.create}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteId !== null} onClose={() => setDeleteId(null)} title={t.admin.deleteProduct} size="sm">
        <p className="text-sm text-antique-sepia/70">
          {t.admin.deleteConfirm}
        </p>
        <div className="flex justify-start gap-3 mt-6">
          <Button variant="secondary" onClick={() => setDeleteId(null)}>{t.admin.cancel}</Button>
          <Button variant="danger" isLoading={deleteMutation.isPending} onClick={() => deleteId && deleteMutation.mutate(deleteId)}>
            {t.admin.delete}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
