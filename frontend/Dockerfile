ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:24-alpine@sha256:31214211871e7c1fed53d111995ec5096f8501697f3206b9e4093202ade151ea AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN npm ci

# Build the application in production mode
RUN npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.0-alpine@sha256:b2e814d28359e77bd0aa5fed1939620075e4ffa0eb20423cc557b375bd5c14ad

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
