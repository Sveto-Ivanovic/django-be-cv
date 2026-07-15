# Build stage
FROM node:22.18-alpine as build

# Set working directory
WORKDIR /app

# Enable pnpm
RUN corepack enable

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml  ./

RUN cat pnpm-workspace.yaml

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Define argument and establish be url
ARG VITE_BE_HOST
ENV VITE_BE_HOST=$VITE_BE_HOST

# Build the app
RUN pnpm build

# Serve stage
FROM nginx:alpine

# Create a non-root user to run nginx
RUN adduser -D -H -u 1001 -s /sbin/nologin webuser

# Create app directory
RUN mkdir -p /app/www

# Copy built assets from build stage
COPY --from=build /app/dist /app/www

# Copy nginx config template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Set correct ownership and permissions
RUN chown -R webuser:webuser /app/www && \
    chmod -R 755 /app/www && \
    # Nginx needs to read and write to these directories
    chown -R webuser:webuser /var/cache/nginx && \
    chown -R webuser:webuser /var/log/nginx && \
    chown -R webuser:webuser /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R webuser:webuser /var/run/nginx.pid && \
    chmod -R 755 /etc/nginx/conf.d

# Expose port (will be overridden by Render)
EXPOSE 3000

# Tell nginx's template processing which variables to replace
ENV NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
ENV NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d
ENV PORT=3000

# Switch to non-root user
USER webuser

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
