FROM node:18-alpine

WORKDIR /app

# Copy package configurations
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source
COPY . .

# Expose Vite's default dev server port
EXPOSE 5173

# Start the application using Vite's development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
