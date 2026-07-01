# syntax=docker/dockerfile:1

# =============================================================================
# Frontend Dockerfile - Antique Marketplace SPA
# =============================================================================
# Multi-stage build:
# Stage 1: Build React app with Vite
# Stage 2: Production (Nginx) or Development (Node.js)

# --- Stage 1: Build ---
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install all dependencies (including dev for build)
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# --- Stage 2: Production (Nginx) ---
FROM nginx:alpine AS production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# --- Stage 3: Development ---
FROM node:20-alpine AS development

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
