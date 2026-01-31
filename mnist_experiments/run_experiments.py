#!/usr/bin/env python3
"""
Experiment Launcher for MNIST Test Suite
Runs experiments in parallel, creates git commits, and logs to WandB
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import time


def run_git_command(cmd, cwd=None):
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return None


def create_experiment_commit(config_path, repo_root):
    """Create a git commit for this experiment"""
    # Load config to get experiment name and description
    with open(config_path, 'r') as f:
        config = json.load(f)

    exp_name = config['experiment_name']
    description = config.get('description', 'No description')

    # Create commit message
    commit_msg = f"""Experiment: {exp_name}

{description}

Configuration changes:
"""
    # Add key config parameters to commit message
    for key in ['hidden_layers', 'learning_rate', 'optimizer', 'batch_size', 'dropout']:
        if key in config:
            commit_msg += f"- {key}: {config[key]}\n"

    # Stage config file
    config_rel_path = os.path.relpath(config_path, repo_root)
    run_git_command(['git', 'add', config_rel_path], cwd=repo_root)

    # Create commit
    result = run_git_command(
        ['git', 'commit', '-m', commit_msg],
        cwd=repo_root
    )

    if result is not None:
        # Get commit hash
        commit_hash = run_git_command(['git', 'rev-parse', 'HEAD'], cwd=repo_root)
        print(f"✓ Created commit {commit_hash[:8]} for {exp_name}")
        return commit_hash
    else:
        print(f"⚠ No changes to commit for {exp_name}")
        return None


def run_single_experiment(config_path, wandb_project, create_commits, repo_root):
    """Run a single experiment"""
    with open(config_path, 'r') as f:
        config = json.load(f)

    exp_name = config['experiment_name']
    print(f"\n{'='*60}")
    print(f"Starting experiment: {exp_name}")
    print(f"Description: {config.get('description', 'N/A')}")
    print(f"{'='*60}\n")

    # Create git commit if requested
    commit_hash = None
    if create_commits:
        commit_hash = create_experiment_commit(config_path, repo_root)

    # Prepare training command
    cmd = [
        sys.executable,  # Use same Python interpreter
        'train.py',
        '--config', config_path,
    ]

    if wandb_project:
        cmd.extend(['--wandb-project', wandb_project])
        cmd.extend(['--wandb-run-name', exp_name])

    # Run training
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            check=True
        )
        duration = time.time() - start_time

        print(f"\n{'='*60}")
        print(f"✓ Completed {exp_name} in {duration:.1f}s")
        print(f"{'='*60}\n")

        # Parse final accuracy from output
        lines = result.stdout.split('\n')
        for line in reversed(lines):
            if 'Val Acc:' in line:
                print(f"Final result: {line.strip()}")
                break

        return {
            'name': exp_name,
            'status': 'success',
            'duration': duration,
            'commit': commit_hash,
            'output': result.stdout
        }

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"✗ Failed {exp_name} after {duration:.1f}s")
        print(f"Error: {e.stderr}")
        print(f"{'='*60}\n")

        return {
            'name': exp_name,
            'status': 'failed',
            'duration': duration,
            'commit': commit_hash,
            'error': e.stderr
        }


def run_experiments_parallel(config_paths, wandb_project, create_commits, repo_root, max_workers):
    """Run experiments in parallel"""
    print(f"\nRunning {len(config_paths)} experiments with {max_workers} parallel workers\n")

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all experiments
        future_to_config = {
            executor.submit(
                run_single_experiment,
                config_path,
                wandb_project,
                create_commits,
                repo_root
            ): config_path
            for config_path in config_paths
        }

        # Collect results as they complete
        for future in as_completed(future_to_config):
            config_path = future_to_config[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Exception in experiment {config_path}: {e}")
                results.append({
                    'name': os.path.basename(config_path),
                    'status': 'exception',
                    'error': str(e)
                })

    return results


def run_experiments_sequential(config_paths, wandb_project, create_commits, repo_root):
    """Run experiments sequentially"""
    print(f"\nRunning {len(config_paths)} experiments sequentially\n")

    results = []
    for config_path in config_paths:
        result = run_single_experiment(config_path, wandb_project, create_commits, repo_root)
        results.append(result)

    return results


def print_summary(results):
    """Print summary of all experiments"""
    print("\n" + "="*80)
    print("EXPERIMENT SUMMARY")
    print("="*80 + "\n")

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    print(f"Total experiments: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"\nTotal duration: {sum(r.get('duration', 0) for r in results):.1f}s")

    if successful:
        print("\n✓ Successful experiments:")
        for r in successful:
            commit_info = f" (commit: {r['commit'][:8]})" if r.get('commit') else ""
            print(f"  - {r['name']}{commit_info} ({r['duration']:.1f}s)")

    if failed:
        print("\n✗ Failed experiments:")
        for r in failed:
            print(f"  - {r['name']} ({r.get('duration', 0):.1f}s)")

    print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Run MNIST experiments for Query.ai test suite'
    )
    parser.add_argument(
        '--configs',
        type=str,
        nargs='+',
        help='Specific config files to run (default: all in configs/)'
    )
    parser.add_argument(
        '--wandb-project',
        type=str,
        default=None,
        help='WandB project name (default: mnist-test-suite)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run experiments in parallel'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--create-commits',
        action='store_true',
        help='Create git commit for each experiment'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be run without executing'
    )

    args = parser.parse_args()

    # Get repository root
    script_dir = Path(__file__).parent.absolute()
    repo_root = script_dir.parent

    # Find config files
    if args.configs:
        config_paths = [Path(c).absolute() for c in args.configs]
    else:
        config_dir = script_dir / 'configs'
        config_paths = sorted(config_dir.glob('*.json'))

    if not config_paths:
        print("No config files found!")
        return 1

    print(f"Found {len(config_paths)} experiments to run")

    # Set default wandb project if not specified
    wandb_project = args.wandb_project or 'mnist-test-suite'

    if args.dry_run:
        print("\nDRY RUN - Would execute:")
        for cp in config_paths:
            with open(cp) as f:
                config = json.load(f)
            print(f"  - {config['experiment_name']}: {config.get('description', 'N/A')}")
        return 0

    # Run experiments
    if args.parallel:
        results = run_experiments_parallel(
            config_paths,
            wandb_project,
            args.create_commits,
            repo_root,
            args.workers
        )
    else:
        results = run_experiments_sequential(
            config_paths,
            wandb_project,
            args.create_commits,
            repo_root
        )

    # Print summary
    print_summary(results)

    # Return non-zero if any failed
    failed = [r for r in results if r['status'] != 'success']
    return len(failed)


if __name__ == '__main__':
    sys.exit(main())
