# Use the official Node.js image as the base image for building
FROM node:18-alpine AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Install dependencies, preferring offline mode but allowing online fallback
RUN npm install --prefer-offline

# Copy the rest of the application files to the container
COPY . .

# Build the React application for production
RUN npm run build

# Remove dev dependencies after build to reduce image size
RUN npm prune --production --prefer-offline

# Use nginx-alpine for smaller footprint in the final image
FROM nginx:alpine

# Copy the built application from the builder stage to the nginx server
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration to optimize for React SPA
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to allow communication to/from the React application
EXPOSE 80

# Start the nginx server
CMD ["nginx", "-g", "daemon off;"]