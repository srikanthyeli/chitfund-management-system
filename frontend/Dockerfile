# ─── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first (layer-cache friendly)
COPY package.json package-lock.json ./

# Install all dependencies (including devDeps needed for build)
RUN npm ci

# Copy source and build production bundle
COPY . .
RUN npm run build


# ─── Stage 2: Production server (Nginx) ────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove default Nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy Vite build output from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom Nginx config: serve SPA + proxy /api → backend service
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
