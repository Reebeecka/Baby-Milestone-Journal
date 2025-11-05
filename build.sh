#!/bin/bash
set -e  # stoppa vid fel

# 🎨 Steg 1: Bygg React (Vite)
echo "🚀 Bygger React frontend..."
cd frontend
npm install
npm run build

# 🔄 Steg 2: Kontrollera build
if [ ! -d "dist" ]; then
    echo "❌ Ingen dist-mapp hittades! Bygget misslyckades."
    exit 1
fi

# 📦 Steg 3: Starta Flask backend
echo "✅ Build klart! Startar Flask backend..."
cd ../backend
export FLASK_ENV=production
python3 app.py
