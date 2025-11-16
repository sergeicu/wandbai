#!/bin/bash
# Quick launcher script for running all experiments

set -e

# Default values
WANDB_PROJECT="mnist-test-suite"
PARALLEL=""
WORKERS=4
CREATE_COMMITS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel)
            PARALLEL="--parallel"
            shift
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --create-commits)
            CREATE_COMMITS="--create-commits"
            shift
            ;;
        --wandb-project)
            WANDB_PROJECT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--parallel] [--workers N] [--create-commits] [--wandb-project PROJECT]"
            exit 1
            ;;
    esac
done

echo "================================"
echo "MNIST Test Suite Launcher"
echo "================================"
echo "WandB Project: $WANDB_PROJECT"
echo "Parallel: ${PARALLEL:-no}"
if [ -n "$PARALLEL" ]; then
    echo "Workers: $WORKERS"
fi
echo "Create commits: ${CREATE_COMMITS:-no}"
echo "================================"
echo ""

# Check if wandb is logged in
if ! wandb login --verify > /dev/null 2>&1; then
    echo "⚠️  WandB not logged in. Please run: wandb login"
    echo "   Or set WANDB_API_KEY environment variable"
    echo ""
    read -p "Continue without WandB logging? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    WANDB_PROJECT=""
fi

# Run experiments
python3 run_experiments.py \
    ${WANDB_PROJECT:+--wandb-project "$WANDB_PROJECT"} \
    $PARALLEL \
    ${PARALLEL:+--workers "$WORKERS"} \
    $CREATE_COMMITS

echo ""
echo "✓ All experiments completed!"
echo "  View results at: https://wandb.ai/YOUR_USERNAME/$WANDB_PROJECT"
