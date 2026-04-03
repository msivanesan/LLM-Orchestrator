# ⛓️ Multi-Stage Build: LLM Orchestrator Frontend
# ═══════════════════════════════════════════════

# Stage 1: Build Phase (Node.js Workspace)
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies first for layer caching
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
# Use build-time ARG to bake environmental vars into the static bundle
# ARG VITE_API_GATEWAY
# ENV VITE_API_GATEWAY=$VITE_API_GATEWAY
RUN npm run build

# Stage 2: Serve Phase (Hardened Nginx)
FROM nginx:stable-alpine
LABEL maintainer="msivanesan"

# Copy the modern static bundle
COPY --from=build /app/dist /usr/share/nginx/html

# Replace default config with SPA-optimized config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
