# Antique Marketplace Frontend

A modern React frontend for the Antique Marketplace backend API.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router v6** for routing
- **TanStack Query** for server state management
- **React Hook Form** + **Zod** for form validation
- **Axios** for API communication
- **React Hot Toast** for notifications
- **Lucide React** for icons

## Features

- Authentication with JWT + refresh token rotation
- Protected routes with role-based access control
- Product listing with search, filters, sorting, and pagination
- Admin dashboard with product CRUD management
- Light/dark theme support
- Responsive design
- Loading skeletons
- Error handling with toast notifications

## Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Project Structure

```
src/
├── api/              # API client and endpoint functions
├── components/       # Reusable UI and layout components
│   ├── auth/         # Authentication-related components
│   ├── layout/       # Layout components (Sidebar, Header, etc.)
│   ├── products/     # Product-specific components
│   └── ui/           # Generic UI components (Button, Input, Modal, etc.)
├── contexts/         # React Context providers
├── hooks/            # Custom React hooks
├── pages/            # Page components
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## API Proxy

The Vite dev server proxies `/api` requests to `http://localhost:8000` (the FastAPI backend).

## Build

```bash
npm run build
```

The build output will be in the `dist/` directory.
