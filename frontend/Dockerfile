ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:25-alpine@sha256:bce79c648e05d584ad9ae2b45ed663ae6f07ebfa9e5fe6f5b7f0165aca06e792 AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.3-alpine@sha256:b23ea6c10814fccb32ac20485c74168ebefa1c3544a3dddfcb33494d24270df8

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --chmod=+x deploy/entrypoint.sh /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
