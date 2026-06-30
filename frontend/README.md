# Frontend

React SPA for the Antique Marketplace application.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite 6** - Build tool
- **Tailwind CSS 3.4** - Styling
- **React Router 6** - Client-side routing
- **TanStack React Query** - Server state management
- **Axios** - HTTP client
- **Zod + React Hook Form** - Form validation
- **react-hot-toast** - Notifications
- **lucide-react** - Icons
- **jalali-moment** - Persian date formatting

## Installation

```bash
cd frontend

# Install dependencies
npm install
```

## Environment Variables

Create a `.env` file in the `frontend/` directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Running

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Pages

| Route | Page | Access |
|-------|------|--------|
| `/` | Products listing | Public |
| `/products/:id` | Product details | Public |
| `/login` | Login | Public |
| `/register` | Register | Public |
| `/cart` | Shopping cart | Protected |
| `/orders` | Orders list | Protected |
| `/orders/:id` | Order details | Protected |
| `/profile` | User profile | Protected |
| `/my-products` | My products | Protected |
| `/admin` | Admin dashboard | Admin only |
| `/admin/products` | Admin products | Admin only |
| `/admin/users` | Admin users | Admin only |

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # Base components (Button, Input, Select, etc.)
│   │   ├── layout/       # Header, Sidebar, Layout
│   │   └── auth/         # ProtectedRoute
│   ├── pages/            # Route pages
│   │   ├── Products.tsx
│   │   ├── ProductDetail.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Cart.tsx
│   │   ├── Orders.tsx
│   │   ├── OrderDetail.tsx
│   │   ├── Profile.tsx
│   │   ├── MyProducts.tsx
│   │   ├── AdminDashboard.tsx
│   │   ├── AdminProducts.tsx
│   │   ├── AdminUsers.tsx
│   │   └── NotFound.tsx
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript type definitions
│   ├── api/              # API client configuration
│   ├── contexts/         # React contexts (AuthContext)
│   ├── App.tsx           # Root component with routing
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── index.html            # HTML template
├── tailwind.config.js    # Tailwind configuration
├── vite.config.ts        # Vite configuration
└── package.json
```

## Styling

The app uses a custom vintage/antique theme defined in `tailwind.config.js`:
- Custom colors: gold, wood, cream, bronze, sepia, parchment, ink
- Custom fonts: Vazirmatn (Persian/Arabic)
- Custom shadows: vintage, vintage-lg, golden
- RTL layout for Persian UI

Custom utility classes in `index.css`:
- `btn-primary`, `btn-secondary`, `btn-danger`
- `input-field`, `card`
- `vintage-border`, `parchment-bg`
