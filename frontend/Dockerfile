ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:24-alpine@sha256:31214211871e7c1fed53d111995ec5096f8501697f3206b9e4093202ade151ea AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN npm ci

# Build the application in production mode
RUN npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.0-alpine@sha256:f741b7f2e82ec8e3daa163b089d48ec163ad0b015d859a1e4f0f2a6202e8cc22

# Copy the build output
COPY --from=build-stage /app/dist /app/dist

# Copy the nginx config
COPY --from=build-stage /app/deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint and configuration setup scripts
COPY --from=build-stage /app/deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["sh","/app/entrypoint.sh"]
