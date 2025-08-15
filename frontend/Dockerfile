ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:24-alpine@sha256:820e86612c21d0636580206d802a726f2595366e1b867e564cbc652024151e8a AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN npm ci

# Build the application in production mode
RUN npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.1-alpine@sha256:c3d2ee1eed702c6f29f2e2f727e93b5cafdc7dec7feef3ad2e6d7c39670853ec

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
