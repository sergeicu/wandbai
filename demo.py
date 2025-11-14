#!/usr/bin/env python3
"""Demo script to test clustering and AI analysis with sample data."""

import pandas as pd
import numpy as np
from clustering import ExperimentCluster
from ai_analysis import AIAnalyzer
import os

# Set random seed for reproducibility
np.random.seed(42)


def generate_sample_runs(n_runs=20):
    """Generate sample experiment data."""
    runs = []

    for i in range(n_runs):
        # Generate sample metrics with different characteristics
        if i < 7:
            # High performance cluster
            accuracy = np.random.uniform(0.90, 0.95)
            loss = np.random.uniform(0.05, 0.15)
            learning_rate = np.random.uniform(0.0001, 0.001)
            cluster_type = "high-perf"
        elif i < 14:
            # Medium performance cluster
            accuracy = np.random.uniform(0.75, 0.85)
            loss = np.random.uniform(0.20, 0.35)
            learning_rate = np.random.uniform(0.001, 0.01)
            cluster_type = "medium-perf"
        else:
            # Low performance/convergence issues
            accuracy = np.random.uniform(0.55, 0.70)
            loss = np.random.uniform(0.40, 0.80)
            learning_rate = np.random.uniform(0.01, 0.1)
            cluster_type = "low-perf"

        run = {
            'id': f"run_{i}",
            'name': f"experiment-{i:03d}",
            'state': 'finished',
            'accuracy': accuracy,
            'loss': loss,
            'val_accuracy': accuracy - np.random.uniform(0.01, 0.05),
            'val_loss': loss + np.random.uniform(0.01, 0.05),
            'learning_rate': learning_rate,
            'epoch': np.random.randint(45, 50),
            'batch_size': np.random.choice([16, 32, 64]),
            'config_learning_rate': learning_rate,
            'config_batch_size': np.random.choice([16, 32, 64]),
            'config_optimizer': np.random.choice(['adam', 'sgd']),
            'runtime': np.random.uniform(100, 500),
            '_true_cluster': cluster_type  # For validation
        }
        runs.append(run)

    return pd.DataFrame(runs)


def test_clustering():
    """Test the clustering functionality."""
    print("=" * 60)
    print("Testing Experiment Clustering")
    print("=" * 60)

    # Generate sample data
    df = generate_sample_runs(20)
    print(f"\nGenerated {len(df)} sample experiment runs")

    # Create clusterer
    clusterer = ExperimentCluster(method='kmeans', n_clusters=3)

    # Cluster the runs
    print("\nClustering experiments...")
    clustered_df = clusterer.cluster_runs(df, metric_cols=['accuracy', 'loss', 'learning_rate'])

    print(f"✓ Clustering complete!")

    # Get cluster summary
    summary = clusterer.get_cluster_summary(clustered_df)
    characteristics = clusterer.get_cluster_characteristics(clustered_df)

    print("\n" + "-" * 60)
    print("Cluster Summary:")
    print("-" * 60)

    for cluster_id, char in characteristics.items():
        cluster_data = summary[cluster_id]
        print(f"\n📊 Cluster {cluster_id}: {char}")
        print(f"   Size: {cluster_data['size']} runs")
        print(f"   Runs: {', '.join(cluster_data['runs'][:3])}{'...' if len(cluster_data['runs']) > 3 else ''}")

        if 'accuracy' in cluster_data['stats']:
            acc_stats = cluster_data['stats']['accuracy']
            print(f"   Accuracy: {acc_stats['mean']:.4f} (±{acc_stats['std']:.4f})")

        if 'loss' in cluster_data['stats']:
            loss_stats = cluster_data['stats']['loss']
            print(f"   Loss: {loss_stats['mean']:.4f} (±{loss_stats['std']:.4f})")

    return clustered_df, summary, characteristics


def test_ai_analysis(clustered_df, summary, characteristics):
    """Test AI analysis (requires API key)."""
    print("\n" + "=" * 60)
    print("Testing AI Analysis")
    print("=" * 60)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_key:
        print("\n⚠️  ANTHROPIC_API_KEY not found in environment")
        print("   Skipping AI analysis test")
        print("   Set your API key to test this feature:")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        return

    print("\n✓ API key found, initializing AI analyzer...")

    try:
        ai = AIAnalyzer(anthropic_key)

        # Get a sample run from the best cluster
        # Find cluster with highest accuracy
        best_cluster_id = None
        best_accuracy = 0

        for cluster_id, stats in summary.items():
            if 'accuracy' in stats['stats']:
                acc = stats['stats']['accuracy']['mean']
                if acc > best_accuracy:
                    best_accuracy = acc
                    best_cluster_id = cluster_id

        cluster_data = summary[best_cluster_id]
        selected_run = clustered_df[clustered_df['cluster'] == best_cluster_id].iloc[0].to_dict()

        print(f"\nAnalyzing Cluster {best_cluster_id}: {characteristics[best_cluster_id]}")
        print(f"Selected run: {selected_run['name']}")

        print("\n🤖 Generating AI insights...")
        analysis = ai.analyze_experiment_cluster(cluster_data, summary, selected_run)

        print("\n" + "-" * 60)
        print("AI Analysis Results:")
        print("-" * 60)

        print(f"\n💡 Summary:")
        print(f"   {analysis.get('summary', 'No summary available')}")

        if analysis.get('insights'):
            print(f"\n🔍 Key Insights:")
            for insight in analysis['insights']:
                print(f"   • {insight}")

        if analysis.get('recommendations'):
            print(f"\n✨ Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   → {rec}")

        print("\n✓ AI analysis complete!")

    except Exception as e:
        print(f"\n❌ Error in AI analysis: {e}")


def main():
    print("\n🔬 Query.ai - Testing Core Functionality\n")

    # Test clustering
    clustered_df, summary, characteristics = test_clustering()

    # Test AI analysis
    test_ai_analysis(clustered_df, summary, characteristics)

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\nTo run the full application:")
    print("  streamlit run app.py")
    print("\nMake sure to set your API keys:")
    print("  export WANDB_API_KEY=your_wandb_key")
    print("  export ANTHROPIC_API_KEY=your_anthropic_key")
    print()


if __name__ == "__main__":
    main()
