FROM node:alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN --mount=type=cache,target=/root/.npm npm ci

COPY frontend/ ./

# ✅ Build برای Production
RUN npm run build

# ✅ نصب serve (یک سرور static ساده)
RUN npm install -g serve

EXPOSE 3000

# ✅ اجرا با serve
CMD ["serve", "-s", "dist", "-l", "3000"]
