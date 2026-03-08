#!/bin/bash
# Setup script for pre-commit hooks
# This script installs and configures pre-commit hooks for the project

set -e  # Exit on any error

echo "🔧 Setting up pre-commit hooks for asyncgateway..."

# Check if pre-commit is available through uv
if ! uv run pre-commit --version &> /dev/null; then
    echo "📦 Installing pre-commit..."
    if command -v uv &> /dev/null; then
        uv add --dev pre-commit
    elif command -v pip &> /dev/null; then
        pip install pre-commit
    else
        echo "❌ Neither uv nor pip found. Please install pre-commit manually:"
        echo "   pip install pre-commit"
        exit 1
    fi
fi

# Install the git hooks
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install

# Install pre-push hooks for more expensive checks
echo "🚀 Installing pre-push hooks..."
uv run pre-commit install --hook-type pre-push

# Run the hooks once to ensure they work
echo "✅ Running pre-commit hooks once to validate setup..."
uv run pre-commit run --all-files || true

echo ""
echo "🎉 Pre-commit hooks are now set up!"
echo ""
echo "📝 Usage:"
echo "  • Hooks will run automatically on 'git commit'"
echo "  • Tests will run automatically on 'git push'"
echo "  • Run all hooks manually: uv run pre-commit run --all-files"
echo "  • Run make premerge manually: uv run pre-commit run make-premerge"
echo "  • Update hooks: uv run pre-commit autoupdate"
echo ""
echo "🔍 What will run:"
echo "  On commit: ruff (lint+format), trailing whitespace, yaml checks, bandit security scan"
echo "  On push: all commit hooks + pytest test suite"
echo "  Manual: make premerge (complete CI pipeline validation)"
echo ""
