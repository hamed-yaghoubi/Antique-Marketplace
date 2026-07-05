FROM node:alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN --mount=type=cache,target=/root/.npm npm ci

COPY frontend/ ./

# ✅ فقط این خط عوض می‌شه
RUN npm run build

# ✅ این خط جدید اضافه می‌شه (برای نصب serve)
RUN npm install -g serve

EXPOSE 3000

# ✅ این خط هم عوض می‌شه
CMD ["serve", "-s", "dist", "-l", "3000"]
