# Simple production Dockerfile for Next.js 15 app on Render
# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Speed up node builds
ENV CI=true \
    NODE_ENV=production

# Recommended for some Next.js native deps
RUN apk add --no-cache libc6-compat

# Install deps with cache
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# System dependency for some images/native modules
RUN apk add --no-cache libc6-compat

# Copy only what's needed to run
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/next.config.mjs ./next.config.mjs
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next

# Expose default port (Render will set $PORT)
EXPOSE 3000

# Start Next.js server, binding to the Render-provided $PORT
CMD ["sh","-c","npm run start -- -p ${PORT:-3000}"]
