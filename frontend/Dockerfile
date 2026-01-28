ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:25-alpine@sha256:260b19691dc84090cf0c7773a38d2bce92e1aa86a184868eaed85675053e8c8e AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.4-alpine@sha256:7d7a15b8a280c661051955f14c2b91fed3e23724ddba18d2f53e8b44e74ab37a

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --chmod=+x deploy/entrypoint.sh /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
