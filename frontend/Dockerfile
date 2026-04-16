ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:25-alpine@sha256:ad82ecad30371c43f4057aaa4800a8ed88f9446553a2d21323710c7b937177fc AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.8-alpine@sha256:8aa63af009a39ecd6c28d61da578a5447378c10bb097a069e3a3e0fb42bb6b19

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --chmod=+x deploy/entrypoint.sh /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
