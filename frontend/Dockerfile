ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:25-alpine@sha256:636c5bc8fa6a7a542bc99f25367777b0b3dd0db7d1ca3959d14137a1ac80bde2 AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.6-alpine@sha256:eb37f58646a901dc7727cf448cae36daaefaba79de33b5058dab79aa4c04aefb

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --chmod=+x deploy/entrypoint.sh /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
