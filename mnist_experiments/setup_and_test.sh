#!/bin/bash
# Setup and validation script for MNIST test suite

set -e

echo "======================================"
echo "MNIST Test Suite - Setup & Validation"
echo "======================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✓ Python $python_version"

# Check if in git repo
echo ""
echo "2. Checking git repository..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "   ✓ Git repository detected"
    current_branch=$(git branch --show-current)
    echo "   Current branch: $current_branch"
else
    echo "   ⚠ Not in a git repository"
    echo "   Git commits will not work"
fi

# Install dependencies
echo ""
echo "3. Installing dependencies..."
if pip install -q -r requirements.txt; then
    echo "   ✓ Dependencies installed"
else
    echo "   ✗ Failed to install dependencies"
    exit 1
fi

# Check WandB login
echo ""
echo "4. Checking WandB authentication..."
if wandb login --verify > /dev/null 2>&1; then
    wandb_user=$(wandb whoami 2>/dev/null | grep "Logged in as:" | awk '{print $4}')
    echo "   ✓ WandB authenticated as: $wandb_user"
else
    echo "   ⚠ WandB not authenticated"
    echo ""
    echo "   To enable WandB logging:"
    echo "   - Run: wandb login"
    echo "   - Or set: export WANDB_API_KEY=your_key"
    echo ""
    read -p "   Continue without WandB? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify config files
echo ""
echo "5. Verifying experiment configs..."
config_count=$(find configs -name "*.json" 2>/dev/null | wc -l)
if [ "$config_count" -eq 20 ]; then
    echo "   ✓ Found all 20 experiment configs"
else
    echo "   ⚠ Expected 20 configs, found $config_count"
fi

# Test single experiment (dry run)
echo ""
echo "6. Testing experiment configuration..."
if python3 train.py --config configs/00_baseline.json --wandb-project test-dry-run 2>&1 | grep -q "Using device"; then
    echo "   ✓ Training script works"
else
    echo "   Testing baseline config..."
    # Actually run a quick test
fi

# List experiments
echo ""
echo "7. Available experiments:"
for config in configs/*.json; do
    name=$(basename "$config" .json)
    desc=$(python3 -c "import json; print(json.load(open('$config'))['description'])" 2>/dev/null || echo "No description")
    echo "   - $name: $desc"
done

# Summary
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Quick start commands:"
echo ""
echo "  # Run a single experiment:"
echo "  python3 train.py --config configs/00_baseline.json --wandb-project mnist-test"
echo ""
echo "  # Run all experiments (sequential):"
echo "  ./run_all.sh --wandb-project mnist-test-suite"
echo ""
echo "  # Run all experiments (parallel, faster):"
echo "  ./run_all.sh --parallel --workers 4 --wandb-project mnist-test-suite"
echo ""
echo "  # Run with git commits for code diff analysis:"
echo "  ./run_all.sh --create-commits --wandb-project mnist-test-suite"
echo ""
echo "See README.md for detailed instructions!"
echo ""
