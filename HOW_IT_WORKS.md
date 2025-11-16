# How Query.ai Works - Technical Deep Dive

## Overview

Query.ai is an AI-powered experiment management platform that connects to Weights & Biases (WandB) projects, intelligently clusters similar experiments, and uses Claude AI to provide actionable insights for machine learning research.

## Architecture Flow

```
User → WandB API → Data Extraction → Clustering → AI Analysis → Insights
```

---

## 1. Data Collection from WandB

### What Gets Fetched

When you load a WandB project, the app fetches up to 100 runs and extracts:

#### **Metadata** (for each run):
- `id`: Unique run identifier
- `name`: Run name (e.g., "experiment-042")
- `state`: Run status (finished, running, failed, crashed)
- `created_at`: Timestamp when run started
- `updated_at`: Last update timestamp
- `runtime`: Total runtime in seconds
- `user`: Username who created the run
- `commit`: Git commit hash (if tracked)
- `tags`: User-defined tags
- `notes`: User notes about the run
- `url`: Link to WandB dashboard

#### **Summary Metrics** (final values):
All numeric metrics logged to WandB, commonly including:
- `accuracy`: Final model accuracy
- `loss`: Final training loss
- `val_accuracy`: Validation accuracy
- `val_loss`: Validation loss
- `epoch`: Number of epochs completed
- `f1_score`: F1 metric (if logged)
- `precision`, `recall`: Classification metrics
- Any custom metrics you've logged

#### **Configuration Parameters**:
All hyperparameters and config values, typically:
- `learning_rate`: Learning rate used
- `batch_size`: Batch size
- `optimizer`: Optimizer type (adam, sgd, etc.)
- `model_architecture`: Model name/type
- `dropout_rate`: Dropout probability
- `weight_decay`: L2 regularization
- Any custom config you've logged

### Example Data Structure

```python
{
    'id': 'abc123',
    'name': 'attention-v3',
    'state': 'finished',
    'created_at': '2024-01-15T10:30:00',
    'runtime': 3600,
    'commit': 'a3f8b2',
    'tags': ['transformer', 'production'],

    # Summary metrics (final values)
    'accuracy': 0.942,
    'loss': 0.142,
    'val_accuracy': 0.938,
    'val_loss': 0.156,
    'epoch': 48,

    # Config (hyperparameters)
    'config_learning_rate': 0.001,
    'config_batch_size': 32,
    'config_optimizer': 'adam',
    'config_num_heads': 16
}
```

---

## 2. Intelligent Clustering

### Clustering Algorithm

**Method**: K-Means (default) or DBSCAN
**Library**: scikit-learn

### Feature Preparation

1. **Feature Selection**:
   - Automatically selects ALL numeric columns
   - Excludes metadata columns: `id`, `name`, `state`, `created_at`, `runtime`, `commit`, `tags`
   - Includes: metrics (accuracy, loss) AND config parameters (learning_rate, batch_size)

2. **Example Features Used**:
   ```python
   [
       'accuracy',           # 0.942
       'loss',              # 0.142
       'val_accuracy',      # 0.938
       'val_loss',          # 0.156
       'epoch',             # 48
       'learning_rate',     # 0.001
       'batch_size',        # 32
       'dropout_rate',      # 0.1
       # ... any other numeric metrics/configs
   ]
   ```

3. **Preprocessing**:
   - Fill missing values with column mean
   - Standardize using StandardScaler (mean=0, std=1)
   - This ensures features with different scales (e.g., accuracy=0.9, batch_size=32) are comparable

### K-Means Clustering

**Parameters**:
- `n_clusters`: User-defined (2-10, default 3)
- `random_state`: 42 (for reproducibility)
- `n_init`: 10 (number of initializations)

**Process**:
1. Initialize k cluster centroids randomly
2. Assign each experiment to nearest centroid
3. Update centroids as mean of assigned experiments
4. Repeat until convergence
5. Return cluster labels (0, 1, 2, ...)

### Cluster Statistics Generated

For each cluster, calculate:

```python
{
    'cluster_0': {
        'size': 7,  # Number of runs in cluster
        'runs': ['experiment-001', 'experiment-002', ...],  # Run names
        'stats': {
            'accuracy': {
                'mean': 0.9251,  # Average accuracy in cluster
                'std': 0.0176,   # Standard deviation
                'min': 0.9000,   # Minimum value
                'max': 0.9500    # Maximum value
            },
            'loss': {
                'mean': 0.1023,
                'std': 0.0325,
                'min': 0.0500,
                'max': 0.1500
            },
            'learning_rate': {
                'mean': 0.0005,
                'std': 0.0002,
                'min': 0.0001,
                'max': 0.0010
            },
            # ... stats for ALL numeric features
        }
    },
    'cluster_1': { ... },
    'cluster_2': { ... }
}
```

### Cluster Characterization

The app automatically labels clusters based on their statistics:

**Rules**:
- **"High accuracy"**: mean accuracy > 0.9
- **"Low accuracy"**: mean accuracy < 0.7
- **"Well converged"**: mean loss < 0.1
- **"Convergence issues"**: mean loss > 0.5
- **"High learning rate"**: mean LR > 0.01
- **"Low learning rate"**: mean LR < 0.0001

**Example Output**:
- Cluster 0: "High accuracy, Well converged"
- Cluster 1: "Medium performance"
- Cluster 2: "Low accuracy, Convergence issues, High learning rate"

---

## 3. AI Analysis with Claude

### What AI Model Is Used

**Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
**Provider**: Anthropic

### Model Capabilities

Claude 3.5 Sonnet is a state-of-the-art language model with:

- **Context Window**: 200,000 tokens (~150,000 words)
  - Can analyze hundreds of experiments at once
  - Retains full context of all clusters and metrics

- **Reasoning Ability**:
  - Pattern recognition across experiments
  - Causal inference (links code/config changes to performance)
  - Statistical analysis understanding
  - Domain knowledge in ML/DL training

- **Output Quality**:
  - Structured JSON responses
  - Actionable recommendations
  - Explains "why" not just "what"

### Exact Data Sent to AI

The AI receives a structured prompt containing:

#### 1. **Cluster Data** (the selected/analyzed cluster):
```json
{
    "size": 7,
    "runs": ["attention-v3", "attention-v2", "baseline-run"],
    "stats": {
        "accuracy": {"mean": 0.9251, "std": 0.0176, "min": 0.90, "max": 0.95},
        "loss": {"mean": 0.1023, "std": 0.0325, "min": 0.05, "max": 0.15},
        "learning_rate": {"mean": 0.0005, "std": 0.0002, "min": 0.0001, "max": 0.001},
        "batch_size": {"mean": 32.0, "std": 0.0, "min": 32, "max": 32},
        "num_heads": {"mean": 14.3, "std": 2.1, "min": 8, "max": 16},
        "epoch": {"mean": 47.4, "std": 1.8, "min": 45, "max": 50}
    }
}
```

#### 2. **All Clusters** (for comparison):
```json
{
    "0": { /* High performance cluster stats */ },
    "1": { /* Medium performance cluster stats */ },
    "2": { /* Low performance cluster stats */ }
}
```

#### 3. **Selected Run Details** (if a specific run is selected):
```json
{
    "id": "abc123",
    "name": "attention-v3",
    "state": "finished",
    "accuracy": 0.942,
    "loss": 0.142,
    "config_learning_rate": 0.001,
    "config_batch_size": 32,
    "config_num_heads": 16,
    "commit": "a3f8b2"
}
```

### The Prompt Sent to Claude

```
You are an AI research assistant analyzing machine learning experiments.
Analyze the following experiment data and provide insights.

## Cluster Data:
{cluster_data as JSON}

## All Clusters (for comparison):
{all_clusters as JSON}

## Selected Run Details:
{selected_run as JSON}

Provide analysis in the following JSON format:
{
  "summary": "Brief 1-2 sentence summary of the key finding",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "key_findings": ["finding 1", "finding 2"]
}

Focus on:
1. Performance differences between clusters
2. Configuration parameters that impact results
3. Convergence patterns
4. Actionable next steps for improving performance
```

### AI Analysis Process

1. **Pattern Recognition**:
   - Identifies which metrics differ most between clusters
   - Spots correlations (e.g., "clusters with higher learning rates converged worse")

2. **Causal Reasoning**:
   - Infers why certain configs led to better performance
   - Explains relationships (e.g., "increasing attention heads from 8→16 improved accuracy by 2.3%")

3. **Comparison**:
   - Compares selected cluster to others
   - Identifies what makes high-performing clusters different

4. **Recommendation Generation**:
   - Suggests concrete next experiments
   - Provides specific parameter values to try
   - Prioritizes by likely impact

### Example AI Output

```json
{
  "summary": "Cluster #3 shows the best performance with 94.2% accuracy. The key difference is the increased attention heads (8→16) in commit a3f8b2.",

  "insights": [
    "High-performing experiments use learning rates between 0.0005-0.001",
    "Batch size of 32 is optimal across all successful runs",
    "Models with 16 attention heads consistently outperform 8 heads by ~2%",
    "Convergence issues in Cluster #2 correlate with learning rates > 0.01"
  ],

  "recommendations": [
    "Try doubling batch size to 64 for faster convergence",
    "Test learning rate decay schedule starting at 0.001",
    "Experiment with 24 or 32 attention heads to see if gains continue",
    "Add gradient clipping to stabilize training in high LR configurations"
  ],

  "key_findings": [
    "Attention heads is the most impactful parameter (2.3% accuracy gain)",
    "Learning rate sweet spot is 0.0005-0.001 for this architecture",
    "All successful runs converged by epoch 45-50"
  ]
}
```

---

## 4. Code Diff Analysis (Optional Feature)

If experiments have git commits tracked:

### Data Extracted

```python
# Git diff between commits
diff = """
diff --git a/model.py b/model.py
index abc123..def456 100644
--- a/model.py
+++ b/model.py
@@ -10,7 +10,7 @@ class Model:
     def __init__(self, config):
         self.config = config
-        self.heads = 8
+        self.heads = 16  # Increased attention heads
         self.layers = config.layers
"""
```

### AI Analysis of Code Changes

The AI can correlate code changes with performance:

```python
# Prompt sent to AI
"""
Analyze how these code changes affected the ML model performance:

## Code Changes:
{diff}

## Metrics Before:
{"accuracy": 0.92, "loss": 0.18}

## Metrics After:
{"accuracy": 0.94, "loss": 0.14}

Provide analysis in JSON format:
{
  "impact_summary": "Brief summary of impact",
  "metric_changes": ["change 1", "change 2"],
  "code_explanation": "What the code changes do",
  "causation_analysis": "Why these changes affected metrics this way"
}
"""
```

**AI Response Example**:
```json
{
  "impact_summary": "Increasing attention heads from 8 to 16 improved accuracy by 2.3% and reduced loss by 22%",
  "metric_changes": [
    "Accuracy increased from 92.0% to 94.2% (+2.2%)",
    "Loss decreased from 0.180 to 0.142 (-21.1%)"
  ],
  "code_explanation": "The change doubled the number of attention heads in the transformer model, allowing it to learn more diverse attention patterns simultaneously",
  "causation_analysis": "More attention heads enable the model to capture both local and global dependencies more effectively. The 8-head configuration was likely bottlenecking the model's representational capacity for this task complexity"
}
```

---

## 5. User Interface Flow

### Step-by-Step User Journey

1. **Authentication** (if enabled):
   - Enter username/password
   - Session persists until logout

2. **Configuration**:
   - Enter WandB API key
   - Enter Anthropic API key (optional)
   - Specify entity (username/team)
   - Specify project name

3. **Load Data**:
   - Click "Load Experiments"
   - App fetches up to 100 runs
   - Displays summary: Total, Completed, Running experiments

4. **Cluster Analysis**:
   - Adjust number of clusters (2-10)
   - Click "Analyze & Cluster"
   - Experiments grouped by similarity
   - Clusters labeled automatically

5. **Explore Results**:
   - Browse clusters in sidebar
   - Click experiment to view details
   - See metrics, configs, code changes

6. **Get AI Insights**:
   - Click "Generate AI Insights"
   - AI analyzes selected run and its cluster
   - Receive structured insights and recommendations

---

## 6. Data Privacy & Security

### API Keys
- Stored in session state (not persisted)
- Never logged or written to disk
- Transmitted over HTTPS to WandB/Anthropic

### Authentication
- Passwords hashed with SHA-256
- Session-based (not persistent)
- Logout clears all session data

### Rate Limiting
- WandB: 60 requests/minute
- Anthropic: 50 requests/minute
- Automatic backoff when limits reached

---

## 7. Technical Implementation Details

### Dependencies

**Core Libraries**:
- `streamlit`: Web UI framework
- `wandb`: WandB API client
- `anthropic`: Claude API client
- `scikit-learn`: Clustering algorithms
- `pandas`: Data manipulation
- `numpy`: Numerical operations

**Infrastructure**:
- `tenacity`: Retry logic with exponential backoff
- `loguru`: Structured logging
- `pytest`: Testing framework

### Error Handling

**Specific Exception Types**:
- `WandBConnectionError`: Network issues
- `WandBAuthenticationError`: Invalid API key
- `WandBProjectNotFoundError`: Project doesn't exist
- `WandBRateLimitError`: Too many requests
- `AIAnalysisError`: Claude API failures
- `ClusteringError`: Clustering failures
- `ValidationError`: Invalid inputs

**Retry Logic**:
- Automatic retry on transient failures
- Exponential backoff: 2s → 4s → 8s
- Up to 3 attempts before failing

### Logging

**Log Levels**:
- `DEBUG`: Detailed execution flow
- `INFO`: Major operations (fetching data, clustering)
- `WARNING`: Transient errors, retries
- `ERROR`: Permanent failures

**Log Format**:
```
2024-01-15 10:30:45 | INFO     | wandb_integration:get_runs:144 - Fetching runs from user/project
2024-01-15 10:30:46 | INFO     | wandb_integration:get_runs:149 - Fetched 42 runs from user/project
```

---

## 8. Performance Characteristics

### Scalability Limits

**Current Limitations**:
- Loads max 100 runs per project (hardcoded)
- All data loaded into memory
- No pagination
- Clustering runs on UI thread (blocks interface)

**Typical Performance**:
- Loading 100 runs: 5-10 seconds
- Clustering 100 runs: 1-2 seconds
- AI analysis: 3-5 seconds (depends on Anthropic API)

**Memory Usage**:
- ~10MB for 100 runs with 20 metrics each
- ~50MB total for app + dependencies

---

## Summary

Query.ai is a sophisticated ML experiment analysis tool that:

1. **Extracts comprehensive data** from WandB (metadata, metrics, configs)
2. **Clusters experiments intelligently** using K-Means on all numeric features
3. **Leverages Claude AI** to analyze patterns and generate actionable insights
4. **Correlates code changes** with performance improvements (if git tracking enabled)
5. **Provides a simple UI** for exploring hundreds of experiments efficiently

The AI receives rich, structured data about experiment clusters and uses advanced reasoning to identify what works, why it works, and what to try next—accelerating ML research by turning raw experimental data into actionable knowledge.
