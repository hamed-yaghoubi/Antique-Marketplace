FROM node:20-slim

WORKDIR /app

# Copy package files first for caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY frontend/ .

EXPOSE 5173

# Run Vite dev server, accessible from outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
