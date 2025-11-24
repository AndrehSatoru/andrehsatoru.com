# Dockerfile para Next.js (produção)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
COPY ../../pnpm-lock.yaml ./pnpm-lock.yaml
COPY . .
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install --frozen-lockfile && pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.mjs ./next.config.mjs
EXPOSE 3000
CMD ["pnpm", "start"]
