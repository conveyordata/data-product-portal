ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:24-alpine@sha256:77f3c4d1f33c17dfa4af4b0add57d86957187873e313c2c37f52831d117645c8 AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN npm ci

# Build the application in production mode
RUN npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.2-alpine@sha256:7c1b9a91514d1eb5288d7cd6e91d9f451707911bfaea9307a3acbc811d4aa82e

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
