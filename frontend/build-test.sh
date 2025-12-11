#!/bin/bash

echo "🔧 Testing frontend build..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ package.json not found. Are you in the frontend directory?"
  exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Create required directories
mkdir -p src/{views,components,stores,services,assets} src/router

# Create minimal files if they don't exist
if [ ! -f "src/main.ts" ]; then
  echo "📝 Creating minimal app structure..."
  cat > src/main.ts << 'EOF'
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
EOF
fi

if [ ! -f "src/App.vue" ]; then
  cat > src/App.vue << 'EOF'
<template>
  <h1>BrandGuard Frontend</h1>
</template>
EOF
fi

if [ ! -f "index.html" ]; then
  cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
  <head>
    <title>BrandGuard</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
EOF
fi

# Try to build
echo "🏗️  Building..."
if npm run build; then
  echo "✅ Build successful!"
  echo "📁 Build output in: dist/"
  ls -la dist/
else
  echo "❌ Build failed!"
  exit 1
fi