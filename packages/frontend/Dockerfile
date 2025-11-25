# Dockerfile para Next.js (produção) - Monorepo
FROM node:20-alpine AS base

# Instalar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# ===== Stage 1: Dependencies =====
FROM base AS deps

WORKDIR /app

# Copiar arquivos do workspace root
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copiar packages
COPY packages/shared-types/package.json ./packages/shared-types/package.json
COPY packages/frontend/package.json ./packages/frontend/package.json

# Instalar dependências
RUN pnpm install --frozen-lockfile

# ===== Stage 2: Builder =====
FROM base AS builder

WORKDIR /app

# Copiar workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copiar packages
COPY packages/shared-types ./packages/shared-types
COPY packages/frontend ./packages/frontend

# Instalar TODAS as dependências no builder
RUN pnpm install --frozen-lockfile

# Build do Next.js
WORKDIR /app/packages/frontend

# Definir variáveis de ambiente para o build
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN pnpm build

# ===== Stage 3: Runner =====
FROM base AS runner

WORKDIR /app

ENV NODE_ENV=production

# Criar usuário não-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copiar arquivos públicos
COPY --from=builder /app/packages/frontend/public ./public

# Copiar standalone build
COPY --from=builder --chown=nextjs:nodejs /app/packages/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/packages/frontend/.next/static ./packages/frontend/.next/static

# Se standalone não incluir shared-types, copiar manualmente
COPY --from=builder --chown=nextjs:nodejs /app/packages/shared-types ./packages/shared-types

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "packages/frontend/server.js"]
