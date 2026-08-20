# ============================================================
# DSA Coach AI - Frontend Dockerfile
# ============================================================

# ------------------------------------------------------------
# Stage 1: Build React/Vite application
# ------------------------------------------------------------

FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first
# This improves Docker layer caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the complete frontend source
COPY . .

# Build production React/Vite application
RUN npm run build


# ------------------------------------------------------------
# Stage 2: Nginx production server
# ------------------------------------------------------------

FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy React production build
COPY --from=builder /app/dist /usr/share/nginx/html

# Use our React Router configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Frontend container listens on port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]