import { useState, useRef, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Plus, Pencil, Trash2, Search, ChevronLeft, ChevronRight, Upload, X, Image } from 'lucide-react'
import { productsApi } from '@/api/products.api'
import { adminApi } from '@/api/admin.api'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { t, toPersianNumbers, formatPrice } from '@/utils/persian'
import { useAuth } from '@/contexts/AuthContext'
import { queryKeys, invalidateProducts, invalidateDashboards } from '@/lib/queryKeys'
import type { ProductCard, ProductFilters, ProductCategory, ProductCreate, ProductUpdate, ProductImage } from '@/types/products'

const categories: Array<{ value: ProductCategory; label: string }> = [
  { value: 'coin', label: 'سکه' },
  { value: 'clock', label: 'ساعت' },
  { value: 'painting', label: 'نقاشی' },
  { value: 'book', label: 'کتاب' },
  { value: 'statue', label: 'مجسمه' },
]

const productSchema = z.object({
  title: z.string().min(1, t.validation.required),
  description: z.string().min(1, t.validation.required),
  price: z.number().gt(0, t.validation.positivePrice),
  quantity: z.number().min(0, t.validation.positiveQuantity),
  category: z.string().min(1, t.validation.required),
})

type ProductForm = z.infer<typeof productSchema>

export function AdminProducts() {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [filters, setFilters] = useState<ProductFilters>({ page: 1, page_size: 10, sort_by: 'created_at', sort_order: 'desc' })
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProductId, setEditingProductId] = useState<number | null>(null)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [existingImages, setExistingImages] = useState<ProductImage[]>([])
  const [isUploading, setIsUploading] = useState(false)

  // Create object URLs for selected files and revoke them on cleanup
  const filePreviewUrls = useMemo(() => {
    return selectedFiles.map((file) => URL.createObjectURL(file))
  }, [selectedFiles])

  useEffect(() => {
    return () => {
      filePreviewUrls.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [filePreviewUrls])

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.products.adminList(filters),
    queryFn: () => productsApi.getProducts(filters),
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
      price: 0,
      quantity: 0,
      category: '',
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: ProductCreate) => productsApi.createProduct(data),
    onSuccess: async (product) => {
      if (selectedFiles.length > 0) {
        setIsUploading(true)
        for (const file of selectedFiles) {
          try {
            await productsApi.uploadImage(product.id, file)
          } catch {
            toast.error(t.admin.imageUploadFailed)
          }
        }
        setIsUploading(false)
      }
      toast.success(t.admin.productCreated)
      invalidateProducts(queryClient)
      invalidateDashboards(queryClient)
      setSelectedFiles([])
      closeModal()
    },
    onError: () => toast.error(t.admin.createFailed),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductUpdate }) => productsApi.updateProduct(id, data),
    onSuccess: async () => {
      if (selectedFiles.length > 0 && editingProductId) {
        setIsUploading(true)
        for (const file of selectedFiles) {
          try {
            await productsApi.uploadImage(editingProductId, file)
          } catch {
            toast.error(t.admin.imageUploadFailed)
          }
        }
        setIsUploading(false)
      }
      toast.success(t.admin.productUpdated)
      invalidateProducts(queryClient)
      invalidateDashboards(queryClient)
      if (editingProductId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(editingProductId) })
      }
      setSelectedFiles([])
      closeModal()
    },
    onError: () => toast.error(t.admin.updateFailed),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => adminApi.deleteProduct(id),
    onSuccess: () => {
      toast.success(t.admin.productDeleted)
      invalidateProducts(queryClient)
      invalidateDashboards(queryClient)
      setDeleteId(null)
    },
    onError: () => toast.error(t.admin.deleteFailed),
  })

  const deleteImageMutation = useMutation({
    mutationFn: ({ productId, imageId }: { productId: number; imageId: number }) =>
      productsApi.deleteImage(productId, imageId),
    onSuccess: (_, variables) => {
      toast.success(t.admin.imageDeleted)
      setExistingImages((prev) => prev.filter((img) => img.id !== variables.imageId))
      if (editingProductId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(editingProductId) })
      }
      invalidateProducts(queryClient)
    },
    onError: () => toast.error(t.admin.imageDeleteFailed),
  })

  const openCreateModal = () => {
    setEditingProductId(null)
    reset({ title: '', description: '', price: 0, quantity: 0, category: '' })
    setSelectedFiles([])
    setExistingImages([])
    setIsModalOpen(true)
  }

  const openEditModal = async (product: ProductCard) => {
    setEditingProductId(product.id)
    const fullProduct = await productsApi.getProduct(product.id)
    reset({
      title: fullProduct.title,
      description: fullProduct.description,
      price: fullProduct.price,
      quantity: fullProduct.quantity,
      category: fullProduct.category,
    })
    setExistingImages(fullProduct.images || [])
    setSelectedFiles([])
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingProductId(null)
    setSelectedFiles([])
    setExistingImages([])
    reset()
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setSelectedFiles((prev) => [...prev, ...files])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeSelectedFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const removeExistingImage = (imageId: number) => {
    if (editingProductId) {
      deleteImageMutation.mutate({ productId: editingProductId, imageId })
    }
  }

  const onSubmit = (formData: ProductForm) => {
    if (editingProductId) {
      const updateData: ProductUpdate = {
        title: formData.title,
        description: formData.description,
        price: formData.price,
        quantity: formData.quantity,
        category: formData.category as ProductCategory,
      }
      updateMutation.mutate({ id: editingProductId, data: updateData })
    } else {
      createMutation.mutate(formData as ProductCreate)
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
          <p className="mt-1 text-sm text-antique-sepia-light">{t.admin.manageSubtitle}</p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="h-4 w-4" />
          {t.admin.addProduct}
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-antique-sepia" />
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
        <TableSkeleton rows={5} cols={5} />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-antique-gold/20 bg-antique-gold/5">
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.product}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.categoryLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.priceLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.admin.stock}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.statusLabel}</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-antique-wood">{t.products.seller}</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-antique-wood">{t.admin.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-antique-gold/10">
              {data?.items.map((product) => (
                <tr key={product.id} className="transition-colors hover:bg-antique-gold/5">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {product.main_image ? (
                        <img src={product.main_image.image_url} alt={product.title} className="h-10 w-10 rounded-lg object-cover border border-antique-gold/20" />
                      ) : (
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-antique-gold/10 border border-antique-gold/20">
                          <Image className="h-4 w-4 text-antique-sepia" />
                        </div>
                      )}
                      <span className="font-semibold text-antique-wood">{product.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4"><Badge variant="info">{categories.find(c => c.value === product.category)?.label ?? product.category}</Badge></td>
                  <td className="px-6 py-4 text-sm font-bold text-antique-wood">{formatPrice(product.price)}</td>
                  <td className="px-6 py-4 text-sm text-antique-wood">{toPersianNumbers(product.quantity)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={product.is_active ? 'success' : 'warning'}>
                      {product.is_active ? t.products.active : t.products.inactive}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-antique-sepia-light">{product.seller ?? '-'}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {product.seller_id === user?.id && (
                        <button onClick={() => openEditModal(product as ProductCard)} className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-antique-gold/10 hover:text-antique-gold transition-colors">
                          <Pencil className="h-4 w-4" />
                        </button>
                      )}
                      <button onClick={() => setDeleteId(product.id)} className="rounded-lg p-1.5 text-antique-sepia-light hover:bg-red-100 hover:text-red-600 transition-colors">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-sm text-antique-sepia-light">
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
          <p className="text-sm text-antique-sepia-light">
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

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingProductId ? t.admin.editProduct : t.admin.createProduct}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label={t.admin.title} placeholder={t.admin.titlePlaceholder} error={errors.title?.message} {...register('title')} />
          <Input label={t.admin.description} placeholder={t.admin.descriptionPlaceholder} error={errors.description?.message} {...register('description')} />
          <div className="grid grid-cols-2 gap-4">
            <Input label={t.admin.priceLabel} type="number" step="0.01" error={errors.price?.message} {...register('price', { valueAsNumber: true })} />
            <Input label={t.admin.quantity} type="number" error={errors.quantity?.message} {...register('quantity', { valueAsNumber: true })} />
          </div>
          <Select label={t.admin.categoryLabel} options={categories} error={errors.category?.message} {...register('category')} />

          <div className="space-y-2">
            <label className="label">{t.admin.images}</label>
            {existingImages.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {existingImages.map((image) => (
                  <div key={image.id} className="relative group">
                    <img src={image.image_url} alt="" className="h-20 w-20 rounded-lg object-cover border border-antique-gold/20" />
                    <button
                      type="button"
                      onClick={() => removeExistingImage(image.id)}
                      className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            {selectedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {selectedFiles.map((_file, index) => (
                  <div key={index} className="relative group">
                    <img src={filePreviewUrls[index]} alt="" className="h-20 w-20 rounded-lg object-cover border border-antique-gold/20" />
                    <button
                      type="button"
                      onClick={() => removeSelectedFile(index)}
                      className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
            <Button type="button" variant="secondary" size="sm" onClick={() => fileInputRef.current?.click()}>
              <Upload className="h-4 w-4" />
              {t.admin.selectImages}
            </Button>
          </div>

          <div className="flex justify-start gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={closeModal}>{t.admin.cancel}</Button>
            <Button type="submit" isLoading={createMutation.isPending || updateMutation.isPending || isUploading}>
              {editingProductId ? t.admin.update : t.admin.create}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteId !== null} onClose={() => setDeleteId(null)} title={t.admin.deleteProduct} size="sm">
        <p className="text-sm text-antique-sepia-light">
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
