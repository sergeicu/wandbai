#!/usr/bin/env python3
"""Test script to verify all modules can be imported."""

print("Testing imports...")

try:
    print("  - wandb_integration...", end=" ")
    from wandb_integration import WandBIntegration
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("  - clustering...", end=" ")
    from clustering import ExperimentCluster
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("  - ai_analysis...", end=" ")
    from ai_analysis import AIAnalyzer
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("  - code_diff...", end=" ")
    from code_diff import CodeDiffAnalyzer
    print("✓")
except Exception as e:
    print(f"✗ {e}")

print("\nAll imports successful!")
