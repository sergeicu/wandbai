import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class ExperimentCluster:
    """Clustering module for grouping similar experiments."""

    def __init__(self, method: str = 'kmeans', n_clusters: int = 3):
        """
        Initialize clustering.

        Args:
            method: Clustering method ('kmeans' or 'dbscan')
            n_clusters: Number of clusters (for kmeans)
        """
        self.method = method
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = []

    def prepare_features(self, df: pd.DataFrame, metric_cols: Optional[List[str]] = None) -> np.ndarray:
        """
        Prepare features for clustering.

        Args:
            df: DataFrame with run data
            metric_cols: Specific metric columns to use (if None, auto-detect numeric columns)

        Returns:
            Scaled feature matrix
        """
        if df.empty:
            return np.array([])

        # Auto-detect numeric columns if not specified
        if metric_cols is None:
            # Get numeric columns, excluding metadata columns
            exclude_cols = ['id', 'name', 'state', 'created_at', 'runtime', 'commit', 'tags']
            metric_cols = [col for col in df.columns
                          if df[col].dtype in ['float64', 'int64']
                          and col not in exclude_cols]

        # Filter to existing columns
        metric_cols = [col for col in metric_cols if col in df.columns]

        if not metric_cols:
            print("Warning: No numeric columns found for clustering")
            return np.array([])

        self.feature_names = metric_cols

        # Extract features and handle missing values
        features = df[metric_cols].copy()
        features = features.fillna(features.mean())

        # Handle case where all values are NaN
        features = features.fillna(0)

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        return scaled_features

    def fit_predict(self, features: np.ndarray) -> np.ndarray:
        """
        Fit clustering model and predict cluster labels.

        Args:
            features: Feature matrix

        Returns:
            Cluster labels
        """
        if features.size == 0 or len(features) == 0:
            return np.array([])

        # Adjust n_clusters if we have fewer samples
        n_samples = features.shape[0]
        n_clusters = min(self.n_clusters, n_samples)

        if self.method == 'kmeans':
            self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = self.model.fit_predict(features)
        elif self.method == 'dbscan':
            self.model = DBSCAN(eps=0.5, min_samples=2)
            labels = self.model.fit_predict(features)
        else:
            raise ValueError(f"Unknown clustering method: {self.method}")

        return labels

    def cluster_runs(self, df: pd.DataFrame, metric_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Cluster runs and add cluster labels to DataFrame.

        Args:
            df: DataFrame with run data
            metric_cols: Specific metric columns to use

        Returns:
            DataFrame with added 'cluster' column
        """
        if df.empty:
            return df

        features = self.prepare_features(df, metric_cols)

        if features.size == 0:
            df['cluster'] = 0
            return df

        labels = self.fit_predict(features)
        df = df.copy()
        df['cluster'] = labels

        return df

    def get_cluster_summary(self, df: pd.DataFrame) -> Dict[int, Dict[str, any]]:
        """
        Generate summary statistics for each cluster.

        Args:
            df: DataFrame with clustered runs

        Returns:
            Dictionary with cluster summaries
        """
        if 'cluster' not in df.columns or df.empty:
            return {}

        summaries = {}

        for cluster_id in df['cluster'].unique():
            cluster_df = df[df['cluster'] == cluster_id]

            # Calculate statistics for numeric columns
            numeric_cols = cluster_df.select_dtypes(include=[np.number]).columns
            stats = {}

            for col in numeric_cols:
                if col != 'cluster':
                    stats[col] = {
                        'mean': float(cluster_df[col].mean()),
                        'std': float(cluster_df[col].std()),
                        'min': float(cluster_df[col].min()),
                        'max': float(cluster_df[col].max())
                    }

            summaries[int(cluster_id)] = {
                'size': len(cluster_df),
                'runs': cluster_df['name'].tolist() if 'name' in cluster_df.columns else [],
                'stats': stats
            }

        return summaries

    def get_cluster_characteristics(self, df: pd.DataFrame) -> Dict[int, str]:
        """
        Generate human-readable characteristics for each cluster.

        Args:
            df: DataFrame with clustered runs

        Returns:
            Dictionary mapping cluster ID to characteristic description
        """
        characteristics = {}
        summaries = self.get_cluster_summary(df)

        for cluster_id, summary in summaries.items():
            stats = summary['stats']

            # Identify distinguishing features
            desc_parts = []

            # Check for high/low accuracy
            if 'accuracy' in stats:
                acc = stats['accuracy']['mean']
                if acc > 0.9:
                    desc_parts.append("High accuracy")
                elif acc < 0.7:
                    desc_parts.append("Low accuracy")

            # Check for convergence
            if 'loss' in stats:
                loss = stats['loss']['mean']
                if loss < 0.1:
                    desc_parts.append("Well converged")
                elif loss > 0.5:
                    desc_parts.append("Convergence issues")

            # Check learning rate
            if 'config_learning_rate' in stats or 'learning_rate' in stats:
                lr_key = 'config_learning_rate' if 'config_learning_rate' in stats else 'learning_rate'
                lr = stats[lr_key]['mean']
                if lr > 0.01:
                    desc_parts.append("High learning rate")
                elif lr < 0.0001:
                    desc_parts.append("Low learning rate")

            if desc_parts:
                characteristics[cluster_id] = ", ".join(desc_parts)
            else:
                characteristics[cluster_id] = f"Cluster {cluster_id}"

        return characteristics

    def reduce_dimensions(self, features: np.ndarray, n_components: int = 2) -> np.ndarray:
        """
        Reduce dimensionality for visualization.

        Args:
            features: Feature matrix
            n_components: Number of components

        Returns:
            Reduced feature matrix
        """
        if features.size == 0 or features.shape[0] < n_components:
            return features

        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(features)

        return reduced
