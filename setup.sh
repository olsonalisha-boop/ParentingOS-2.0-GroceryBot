#!/bin/bash

# Milwaukee Shopping Automation Setup Script
# This script sets up your shopping automation system

echo "🛒 Milwaukee Shopping Automation Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p output
mkdir -p scrapers
mkdir -p automation
mkdir -p .github/workflows

# Check if shopping list exists
if [ ! -f "data/shopping_list.csv" ]; then
    echo "📝 Sample shopping list created in data/shopping_list.csv"
    echo "   Please edit this file with your regular shopping items."
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."
python3 -c "import aiohttp, asyncio, json; print('✅ Core modules imported successfully')"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit data/shopping_list.csv with your shopping items"
    echo "2. Run: python automation/find_deals.py"
    echo "3. Check the output/ folder for your shopping report"
    echo ""
    echo "To set up GitHub automation:"
    echo "1. Create a GitHub account at github.com"
    echo "2. Click 'Fork' on this repository"
    echo "3. Enable GitHub Actions in your fork"
    echo "4. The automation will run daily at 6 AM CST"
    echo ""
    echo "For help, see README.md"
else
    echo "❌ Installation test failed. Please check error messages above."
    exit 1
fi
