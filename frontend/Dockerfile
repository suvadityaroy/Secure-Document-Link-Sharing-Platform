FROM nginx:alpine

# Workdir for static content
WORKDIR /usr/share/nginx/html

# Copy static files
COPY . .

# Install bash for entrypoint script
RUN apk add --no-cache bash

# Copy simple nginx config (no templating needed for public API)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Inject API_BASE into index.html at container start
COPY docker-entrypoint.sh /docker-entrypoint.d/99-inject-env.sh
RUN chmod +x /docker-entrypoint.d/99-inject-env.sh

# Expose default web port
EXPOSE 80
