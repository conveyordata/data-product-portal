ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} node:24-alpine@sha256:6ff78d6d45f2614fe0da54756b44a7c529a15ebcaf9832fab8df036b1d466e73 AS build-stage

WORKDIR /app
COPY . .

# Install all the dependencies
RUN npm ci

# Build the application in production mode
RUN npm run build:prd

# Use official nginx image as the base image
FROM --platform=${PLATFORM} nginx:1.29.2-alpine@sha256:52175fc0394e97029664721dfdb76a8af1e3045532ab5fb2249e555d50f347bc

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
