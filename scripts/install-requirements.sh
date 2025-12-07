# brandguard/scripts/install-requirements.sh
#!/bin/bash

set -e

echo "🚀 Installing BrandGuard Requirements..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Install pip-tools (optional but recommended)
python -m pip install --upgrade pip pip-tools

# Install production requirements
echo "📥 Installing production requirements..."
pip install -r requirements.txt

# Verify installations
echo "✅ Verifying installations..."
python -c "
import importlib
modules = [
    'fastapi', 'sqlalchemy', 'redis', 'torch', 'transformers',
    'scikit-learn', 'pandas', 'numpy', 'pytest', 'black'
]

failed = []
for module in modules:
    try:
        importlib.import_module(module)
        print(f'✅ {module}')
    except ImportError:
        failed.append(module)
        print(f'❌ {module}')

if failed:
    print(f'\n❌ Failed modules: {failed}')
    exit(1)
else:
    print('\n🎉 All requirements installed successfully!')
"

# Optional: Install development requirements
if [ "$1" == "--dev" ]; then
    echo "📚 Installing development requirements..."
    pip install -r requirements-dev.txt
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Available commands:"
echo "  source venv/bin/activate    # Activate virtual environment"
echo "  python -m pytest           # Run backend tests"
echo "  cd frontend && npm install # Install frontend dependencies"
echo "  docker-compose up -d         # Start production services"