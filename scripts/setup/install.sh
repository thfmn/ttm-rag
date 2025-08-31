#!/bin/bash
set -e

echo "🚀 Setting up Thai Traditional Medicine RAG Bot environment..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv --python 3.13

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔍 Setting up pre-commit hooks..."
pre-commit install

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Download Thai language models
echo "🇹🇭 Installing Thai language models..."
python -c "
import pythainlp
pythainlp.corpus.download('thai2fit_wv')
"

# Install spaCy Thai model (if available)
python -m spacy download th_core_news_sm || echo "⚠️  Thai spaCy model not available, using multilingual model"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Set up your database: make db-setup"
echo "3. Run tests: make test"
echo "4. Start development server: make dev"
