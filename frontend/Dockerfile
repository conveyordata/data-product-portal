ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:25-alpine@sha256:b9b5737eabd423ba73b21fe2e82332c0656d571daf1ebf19b0f89d0dd0d3ca93 AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.5-alpine@sha256:1d13701a5f9f3fb01aaa88cef2344d65b6b5bf6b7d9fa4cf0dca557a8d7702ba

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --chmod=+x deploy/entrypoint.sh /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
