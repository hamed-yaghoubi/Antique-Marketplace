import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Products } from '@/pages/Products'
import { ProductDetail } from '@/pages/ProductDetail'
import { Cart } from '@/pages/Cart'
import { Orders } from '@/pages/Orders'
import { OrderDetail } from '@/pages/OrderDetail'
import { Profile } from '@/pages/Profile'
import { MyProducts } from '@/pages/MyProducts'
import { AdminDashboard } from '@/pages/AdminDashboard'
import { AdminProducts } from '@/pages/AdminProducts'
import { NotFound } from '@/pages/NotFound'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<Layout />}>
                <Route path="/" element={<Products />} />
                <Route path="/products/:id" element={<ProductDetail />} />
                <Route element={<ProtectedRoute />}>
                  <Route path="/cart" element={<Cart />} />
                  <Route path="/orders" element={<Orders />} />
                  <Route path="/orders/:id" element={<OrderDetail />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/my-products" element={<MyProducts />} />
                  <Route element={<ProtectedRoute requireAdmin />}>
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/admin/products" element={<AdminProducts />} />
                  </Route>
                </Route>
              </Route>
              <Route path="*" element={<NotFound />} />
            </Routes>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 3000,
                style: {
                  borderRadius: '12px',
                  background: '#4A2C2A',
                  color: '#F5E6D3',
                  fontFamily: 'Vazirmatn, system-ui, sans-serif',
                  direction: 'rtl',
                },
              }}
            />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
