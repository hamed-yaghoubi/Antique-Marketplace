import moment from 'jalali-moment'

const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']

export function toPersianNumbers(str: string | number): string {
  return String(str).replace(/\d/g, (d) => persianDigits[parseInt(d)] ?? d)
}

export function formatJalali(dateString: string): string {
  return moment(dateString).locale('fa').format('jYYYY/jMM/jDD')
}

export function formatJalaliDateTime(dateString: string): string {
  return moment(dateString).locale('fa').format('jYYYY/jMM/jDD  HH:mm')
}

export function formatPrice(amount: number): string {
  const formatted = new Intl.NumberFormat('fa-IR').format(amount)
  return `${toPersianNumbers(formatted)} ریال`
}

export const t = {
  nav: {
    products: 'محصولات',
    cart: 'سبد خرید',
    admin: 'مدیریت',
    dashboard: 'داشبورد',
    manageProducts: 'مدیریت محصولات',
  },
  auth: {
    loginTitle: 'بازارچه عتیقه',
    loginSubtitle: 'به حساب خود وارد شوید',
    username: 'نام کاربری',
    usernamePlaceholder: 'نام کاربری خود را وارد کنید',
    password: 'رمز عبور',
    passwordPlaceholder: 'رمز عبور خود را وارد کنید',
    rememberMe: 'مرا به خاطر بسپار',
    signIn: 'ورود',
    logout: 'خروج',
    welcomeBack: 'خوش آمدید!',
    loginFailed: 'خطا در ورود',
  },
  products: {
    title: 'محصولات',
    subtitle: 'مجموعه عتیقه‌های ما را مرور کنید',
    search: 'جستجوی محصولات...',
    filters: 'فیلترها',
    category: 'دسته‌بندی',
    allCategories: 'همه دسته‌بندی‌ها',
    minPrice: 'حداقل قیمت',
    maxPrice: 'حداکثر قیمت',
    status: 'وضعیت',
    active: 'فعال',
    inactive: 'غیرفعال',
    all: 'همه',
    minStock: 'حداقل موجودی',
    maxStock: 'حداکثر موجودی',
    sortBy: 'مرتب‌سازی بر اساس',
    dateCreated: 'تاریخ ایجاد',
    price: 'قیمت',
    name: 'نام',
    ascending: 'صعودی',
    descending: 'نزولی',
    product: 'محصول',
    sku: 'کد کالا',
    categoryLabel: 'دسته‌بندی',
    priceLabel: 'قیمت',
    statusLabel: 'وضعیت',
    noImage: 'بدون تصویر',
    noProducts: 'محصولی یافت نشد',
    showing: 'نمایش',
    to: 'تا',
    from: 'از',
    results: 'نتیجه',
    page: 'صفحه',
    of: 'از',
  },
  admin: {
    dashboardTitle: 'داشبورد مدیریت',
    dashboardSubtitle: 'نمای کلی بازارچه شما',
    totalProducts: 'کل محصولات',
    activeProducts: 'محصولات فعال',
    categories: 'دسته‌بندی‌ها',
    totalValue: 'ارزش کل',
    manageTitle: 'مدیریت محصولات',
    manageSubtitle: 'ایجاد، ویرایش و حذف محصولات',
    addProduct: 'افزودن محصول',
    editProduct: 'ویرایش محصول',
    createProduct: 'ایجاد محصول',
    deleteProduct: 'حذف محصول',
    deleteConfirm: 'آیا از حذف این محصول اطمینان دارید؟ این عمل قابل بازگشت نیست.',
    title: 'عنوان',
    titlePlaceholder: 'عنوان محصول',
    description: 'توضیحات',
    descriptionPlaceholder: 'توضیحات محصول',
    skuLabel: 'کد کالا',
    skuPlaceholder: 'کد-۰۰۱',
    priceLabel: 'قیمت',
    quantity: 'تعداد',
    categoryLabel: 'دسته‌بندی',
    sellerId: 'شناسه فروشنده',
    activeLabel: 'فعال',
    cancel: 'انصراف',
    create: 'ایجاد',
    update: 'به‌روزرسانی',
    delete: 'حذف',
    productCreated: 'محصول با موفقیت ایجاد شد',
    productUpdated: 'محصول با موفقیت به‌روزرسانی شد',
    productDeleted: 'محصول با موفقیت حذف شد',
    createFailed: 'خطا در ایجاد محصول',
    updateFailed: 'خطا در به‌روزرسانی محصول',
    deleteFailed: 'خطا در حذف محصول',
    stock: 'موجودی',
    actions: 'عملیات',
  },
  validation: {
    required: 'این فیلد الزامی است',
    positivePrice: 'قیمت باید مثبت باشد',
    positiveQuantity: 'تعداد باید مثبت باشد',
  },
  notFound: {
    title: '۴۰۴',
    message: 'صفحه مورد نظر یافت نشد',
    description: 'صفحه‌ای که به دنبال آن هستید وجود ندارد یا منتقل شده است.',
    backToHome: 'بازگشت به صفحه اصلی',
  },
  common: {
    loading: 'در حال بارگذاری...',
    error: 'خطا',
    save: 'ذخیره',
    edit: 'ویرایش',
    delete: 'حذف',
    confirm: 'تأیید',
    cancel: 'انصراف',
  },
  layout: {
    marketplace: 'بازارچه',
    admin: 'مدیریت',
  },
}
