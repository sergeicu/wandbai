# Query.ai - Integrated Platform (Jan 31 Merge)

**Query** is an AI-powered experiment management platform that helps ML researchers analyze metrics, code diffs, and results to cluster runs, generate insights, and suggest next steps.

This merge integrates two components:
1. **Query.ai App** - The Flask-based analysis platform
2. **MNIST Test Suite** - Reproducible experiments for validation

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
cd mnist_experiments && pip install -r requirements.txt && cd ..
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY: For AI analysis
# - WANDB_API_KEY: Your Weights & Biases key
```

### 3. Run Experiments (Optional - skip if you already have WandB runs)

```bash
cd mnist_experiments
./run_all.sh
```

This runs 20 MNIST experiments with different hyperparameters and logs them to WandB.

### 4. Start Query.ai

```bash
python app.py
```

Open http://localhost:5000 in your browser.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                           WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Generate Experiments          Step 2: Analyze in Query.ai  │
│  ┌─────────────────────────┐          ┌─────────────────────────┐  │
│  │  mnist_experiments/     │          │       Query.ai App      │  │
│  │                         │          │                         │  │
│  │  20 configs  ───────────┼────┐     │   ┌─────────────────┐   │  │
│  │  ├── 00_baseline.json   │    │     │   │   WandB API     │   │  │
│  │  ├── 01_arch_deeper.json│    │     │   │   (fetch runs)  │   │  │
│  │  ├── ...                │    │     │   └────────┬────────┘   │  │
│  │  └── 19_optimal_tuned   │    │     │            │             │  │
│  │                         │    │     │            ▼             │  │
│  │  ./run_all.sh           │    │     │   ┌─────────────────┐   │  │
│  │  trains 20 models ──────┼────┘     │   │ AI Analysis     │   │  │
│  │  logs to WandB          │          │   │ (clustering,    │   │  │
│  └─────────────────────────┘          │   │  insights)      │   │  │
│                                      │   └────────┬────────┘   │  │
│                                      │            │             │  │
│                                      │            ▼             │  │
│                                      │   ┌─────────────────┐   │  │
│                                      │   │  Web Dashboard  │   │  │
│                                      │   │  (Flask app)    │   │  │
│                                      │   └─────────────────┘   │  │
│                                      └─────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### The Two Components

#### 1. MNIST Test Suite (`mnist_experiments/`)

Generates reproducible ML experiments to test Query.ai's capabilities.

**Contains:**
- 20 experiment configurations testing different hyperparameters
- `train.py` - PyTorch MNIST training script
- `run_experiments.py` - Orchestrates all experiments
- `run_all.sh` - One-command execution

**Experiment Variations:**
| Config | What It Tests |
|--------|---------------|
| `00_baseline` | Default architecture |
| `01-04` | Architecture changes (deeper, wider, dropout, batchnorm) |
| `05-07` | Learning rates (0.0001, 0.001, 0.01) |
| `08-09` | Optimizers (SGD, RMSprop) |
| `10-11` | Batch sizes (32, 256) |
| `12-16` | Regularization (L2, schedulers, augmentation, early stopping) |
| `17-19` | Best combinations & edge cases |

**Expected Output:**
- 20 WandB runs with different metrics
- Naturally forms 4-5 clusters (high-performing, baseline, poor, overfitting)
- See `mnist_experiments/EXPECTED_CLUSTERS.md` for details

#### 2. Query.ai App (Root Directory)

Analyzes WandB runs using AI to provide insights.

**Key Files:**
| File | Purpose |
|------|---------|
| `app.py` | Flask web server |
| `wandb_integration.py` | Fetches runs from WandB API |
| `ai_analysis.py` | OpenAI-powered clustering and insights |
| `clustering.py` | K-means clustering algorithm |
| `code_diff.py` | Analyzes code differences between runs |

**Features:**
- **Fetch runs** from your WandB projects
- **Cluster experiments** automatically by performance patterns
- **AI insights** explaining what worked and why
- **Code diffs** showing what changed between runs
- **Run comparison** side-by-side

---

## Example Usage

### Running Everything End-to-End

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 2. Generate test data (20 MNIST experiments)
cd mnist_experiments
./run_all.sh
cd ..

# 3. Start Query.ai
python app.py
```

Then open http://localhost:5000:
1. Enter your WandB project name
2. Click "Fetch Runs"
3. View clustered experiments with AI insights

---

## Project Structure

```
wandbai/
├── app.py                      # Flask web application
├── wandb_integration.py        # WandB API client
├── ai_analysis.py              # AI analysis (OpenAI)
├── clustering.py               # K-means clustering
├── code_diff.py                # Code diff analysis
│
├── mnist_experiments/          # Test experiment suite
│   ├── configs/                # 20 experiment configs
│   │   ├── 00_baseline.json
│   │   ├── 01_arch_deeper.json
│   │   └── ... (20 total)
│   ├── train.py                # Training script
│   ├── run_experiments.py      # Orchestrator
│   ├── run_all.sh              # One-command runner
│   ├── EXPECTED_CLUSTERS.md    # Expected analysis results
│   └── README.md               # Detailed docs
│
├── tests/                      # Pytest test suite
│   └── test_wandb_integration.py
│
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── HOW_IT_WORKS.md             # Technical deep-dive
├── QUICKSTART.md               # Original quick start
└── FUTURE_WORK.md              # Planned features
```

---

## API Endpoints

Query.ai exposes these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/runs` | GET | Fetch runs from WandB |
| `/api/cluster` | POST | Cluster runs by similarity |
| `/api/analyze` | POST | Get AI insights on runs |
| `/api/diff` | GET | Compare code between runs |
| `/api/compare` | POST | Side-by-side run comparison |

---

## Expected Clustering Results

When analyzing the 20 MNIST experiments, Query.ai should discover:

**Cluster 1: High Performance (5 runs)**
- Best combined configs: `17_best_combined`, `19_optimal_tuned`
- Accuracy: 97.8-98.5%
- Uses: LR scheduling + regularization + batch normalization

**Cluster 2: Good Performance (10 runs)**
- Solid baseline: `00_baseline`, `02_arch_wider`, etc.
- Accuracy: 96.5-97.5%
- Uses: Adam optimizer, moderate LR

**Cluster 3: Poor Performance (3 runs)**
- Too high LR, wrong optimizer
- Accuracy: <95%

**Cluster 4: Overfitting (2 runs)**
- Large models without regularization
- High train accuracy, low val accuracy

See `mnist_experiments/EXPECTED_CLUSTERS.md` for full details.

---

## Configuration Files

Each experiment config is a JSON file:

```json
{
  "name": "00_baseline",
  "description": "Baseline 2-layer MLP",
  "architecture": {
    "hidden_layers": [128, 64],
    "dropout": 0.0,
    "batch_norm": false
  },
  "training": {
    "epochs": 10,
    "batch_size": 64,
    "learning_rate": 0.001,
    "optimizer": "adam"
  }
}
```

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Experiment Configs

1. Create new JSON in `mnist_experiments/configs/`
2. Follow the existing schema
3. Run with: `python mnist_experiments/run_experiments.py configs/your_config.json`

---

## Branch History

This merge combines:

1. **`claude/wandb-integration-app`** - Core Query.ai platform
   - Flask app with WandB integration
   - AI-powered clustering and analysis
   - 5 commits, ~4,464 lines

2. **`claude/mnist-test-suite-design`** - MNIST test experiments
   - 20 reproducible experiment configs
   - Training and orchestration scripts
   - 2 commits, ~3,179 lines

**Merge Date:** January 31, 2026
**Branch:** `jan31-merge`

---

## Next Steps

1. Configure your `.env` with API keys
2. Run `./mnist_experiments/run_all.sh` to generate data
3. Start the app: `python app.py`
4. Open http://localhost:5000

For questions or issues, see the documentation in:
- `HOW_IT_WORKS.md` - Technical details
- `FUTURE_WORK.md` - Planned enhancements
- `mnist_experiments/README.md` - Experiment suite docs
