# MNIST Test Suite for Query.ai Validation

A comprehensive test suite designed to generate realistic ML experiment data for validating the Query.ai experiment management platform.

## 🎯 Purpose

This test suite simulates a real ML researcher's workflow by running 20 carefully designed MNIST experiments that vary:
- Architecture (depth, width, regularization)
- Hyperparameters (learning rate, batch size, optimizer)
- Training strategies (schedulers, augmentation, early stopping)

Each experiment creates:
- **Separate git commit** - to test code diff analysis
- **Separate WandB run** - to test experiment clustering and insights
- **Diverse performance metrics** - to test AI analysis quality

## 📊 Experiment Design

### Category 1: Architecture Variations (5 experiments)

| Experiment | Changes | Expected Performance |
|------------|---------|---------------------|
| `00_baseline` | 2 layers (128, 64), no regularization | ~97% val accuracy (baseline) |
| `01_arch_deeper` | 4 layers (128, 128, 64, 64) | Similar to baseline, may converge slower |
| `02_arch_wider` | Wider layers (256, 128) | ~97.5% val accuracy (slight improvement) |
| `03_arch_dropout` | Add dropout (0.2) | ~97-97.5% (better generalization) |
| `04_arch_batchnorm` | Add batch normalization | ~97.5-98% (more stable training) |

**What Query.ai should detect:**
- Wider networks and batch norm improve performance
- Dropout helps generalization (train/val gap)
- Depth alone doesn't help for MNIST

---

### Category 2: Learning Rate Variations (4 experiments)

| Experiment | LR | Expected Performance |
|------------|-----|---------------------|
| `00_baseline` | 0.001 (baseline) | ~97% val accuracy |
| `05_lr_very_low` | 0.0001 | ~90-95% (under-trained after 10 epochs) |
| `06_lr_medium` | 0.01 | ~97-98% (faster convergence) |
| `07_lr_high` | 0.1 | ~85-90% (unstable, poor convergence) |

**What Query.ai should detect:**
- LR=0.001-0.01 is the sweet spot
- Too low LR → slow convergence, under-fitting
- Too high LR → training instability, worse results
- Clear correlation between LR and final loss

---

### Category 3: Optimizer Variations (3 experiments)

| Experiment | Optimizer | LR | Expected Performance |
|------------|-----------|-----|---------------------|
| `00_baseline` | Adam | 0.001 | ~97% (baseline) |
| `08_opt_sgd` | SGD + momentum | 0.01 | ~96-97% (needs higher LR) |
| `09_opt_rmsprop` | RMSprop | 0.001 | ~97% (similar to Adam) |

**What Query.ai should detect:**
- Adam works well with default LR
- SGD requires careful LR tuning
- Optimizer choice has modest impact for MNIST

---

### Category 4: Batch Size Variations (3 experiments)

| Experiment | Batch Size | Expected Performance |
|------------|------------|---------------------|
| `10_batch_small` | 32 | ~97% (slower but stable) |
| `00_baseline` | 128 (baseline) | ~97% |
| `11_batch_large` | 512 | ~96-97% (faster but noisier) |

**What Query.ai should detect:**
- Batch size has minimal impact on final accuracy
- Smaller batches → more training time
- Larger batches → faster epochs but may need LR adjustment

---

### Category 5: Advanced Training Strategies (5 experiments)

| Experiment | Strategy | Expected Performance |
|------------|----------|---------------------|
| `12_reg_l2` | L2 regularization (weight_decay=0.001) | ~97-97.5% (better generalization) |
| `13_scheduler_step` | Step LR decay | ~97.5-98% (better final accuracy) |
| `14_scheduler_cosine` | Cosine annealing | ~97.5-98% (smooth convergence) |
| `15_data_augmentation` | Random rotations/translations | ~97-97.5% (robust model) |
| `16_early_stopping` | Stop when val loss plateaus | ~97% (efficient training) |

**What Query.ai should detect:**
- LR scheduling improves final performance
- Data augmentation helps generalization
- Early stopping reduces training time without hurting accuracy

---

### Category 6: Combined Experiments (2 experiments)

| Experiment | Strategy | Expected Performance |
|------------|----------|---------------------|
| `17_best_combined` | Wider net + dropout + batch norm + scheduler + augmentation | **~98-98.5%** (best performance) |
| `18_overfit_scenario` | Very deep (5 layers), no regularization, small batch | ~98% train, ~96% val (overfitting) |
| `19_optimal_tuned` | Well-tuned hyperparameters based on best results | **~98-98.5%** (best overall) |

**What Query.ai should detect:**
- Combining best practices yields best results
- `17_best_combined` and `19_optimal_tuned` should cluster together
- `18_overfit_scenario` shows high train/val gap
- Clear progression from baseline → optimized

---

## 🚀 Quick Start

### 1. Setup

```bash
cd mnist_experiments

# Install dependencies
pip install -r requirements.txt

# Login to WandB
wandb login
```

### 2. Run Experiments

**Option A: Run all experiments sequentially**
```bash
./run_all.sh --wandb-project mnist-test-suite
```

**Option B: Run in parallel (faster, 4 workers)**
```bash
./run_all.sh --parallel --workers 4 --wandb-project mnist-test-suite
```

**Option C: Run with git commits (for code diff analysis)**
```bash
./run_all.sh --create-commits --wandb-project mnist-test-suite
```

**Option D: Run specific experiments**
```bash
python3 run_experiments.py \
    --configs configs/00_baseline.json configs/17_best_combined.json \
    --wandb-project mnist-test-suite
```

### 3. Run a Single Experiment

```bash
python3 train.py \
    --config configs/00_baseline.json \
    --wandb-project mnist-test-suite \
    --wandb-run-name baseline-test
```

---

## 📈 Expected Results Summary

### Performance Clusters (for Query.ai to discover)

**Cluster 1: High Performance (98-98.5% val accuracy)**
- `17_best_combined`
- `19_optimal_tuned`
- `13_scheduler_step`
- `14_scheduler_cosine`

**Common characteristics:**
- LR scheduling enabled
- Batch normalization or regularization
- LR in range 0.001-0.01

**Cluster 2: Good Performance (97-97.5% val accuracy)**
- `00_baseline`
- `02_arch_wider`
- `03_arch_dropout`
- `04_arch_batchnorm`
- `06_lr_medium`
- `08_opt_sgd`
- `09_opt_rmsprop`
- `10_batch_small`
- `12_reg_l2`
- `15_data_augmentation`

**Common characteristics:**
- Reasonable hyperparameters
- Basic or no regularization
- LR around 0.001-0.01

**Cluster 3: Moderate Performance (90-96% val accuracy)**
- `05_lr_very_low` (slow convergence)
- `07_lr_high` (unstable training)
- `01_arch_deeper` (unnecessary complexity)
- `11_batch_large` (may need LR adjustment)

**Common characteristics:**
- Suboptimal hyperparameters
- Too high or too low LR
- Training inefficiencies

**Cluster 4: Overfitting (high train, lower val)**
- `18_overfit_scenario`

**Characteristics:**
- High train accuracy (98%+)
- Lower val accuracy (~96%)
- No regularization, very deep network

---

## 🔍 What Query.ai Should Discover

### Key Insights (AI should identify)

1. **Learning Rate is Critical**
   - "Experiments with LR=0.001-0.01 consistently outperform others"
   - "LR=0.1 causes training instability (loss > 0.5)"
   - "LR=0.0001 leads to under-training within 10 epochs"

2. **Regularization Helps**
   - "Dropout, batch norm, and L2 regularization improve val accuracy by 0.5-1%"
   - "Experiment 18 shows clear overfitting without regularization"

3. **LR Scheduling is Key to Best Results**
   - "Top 2 experiments (17, 19) both use LR scheduling"
   - "Cosine annealing and step decay both improve final accuracy"

4. **Architecture Optimizations**
   - "Wider networks (256/128) outperform deeper networks (4 layers)"
   - "Batch normalization adds 0.5% val accuracy boost"

5. **Combined Approaches Win**
   - "Combining best practices (exp 17, 19) achieves 98%+ accuracy"
   - "Single optimizations add 0.5-1% each, combined add 1.5-2%"

### Code Diff Analysis (if commits enabled)

Query.ai should correlate code changes with performance:

- **Commit for 17_best_combined**: Adding batch norm + dropout + wider layers
  - **Impact**: +1.5% val accuracy vs baseline

- **Commit for 04_arch_batchnorm**: Adding `batch_norm=true`
  - **Impact**: +0.5% val accuracy, more stable training

- **Commit for 13_scheduler_step**: Adding LR scheduler
  - **Impact**: +0.5-1% val accuracy in later epochs

---

## 📁 Project Structure

```
mnist_experiments/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── train.py                    # Main training script
├── run_experiments.py          # Parallel experiment launcher
├── run_all.sh                  # Simple bash wrapper
├── configs/                    # 20 experiment configurations
│   ├── 00_baseline.json
│   ├── 01_arch_deeper.json
│   ├── ...
│   └── 19_optimal_tuned.json
├── data/                       # MNIST dataset (auto-downloaded)
└── results/                    # (optional) saved models/logs
```

---

## 🧪 Validation Checklist for Query.ai

Use this checklist to verify Query.ai works correctly:

### ✅ Data Loading
- [ ] Fetches all 20 runs from WandB
- [ ] Extracts all metrics (train_loss, train_accuracy, val_loss, val_accuracy, learning_rate)
- [ ] Extracts all config parameters (learning_rate, batch_size, optimizer, etc.)
- [ ] Handles git commit hashes (if enabled)

### ✅ Clustering
- [ ] Clusters experiments into 3-4 meaningful groups
- [ ] High-performance experiments cluster together (17, 19, 13, 14)
- [ ] Poor-performance experiments cluster together (5, 7)
- [ ] Identifies key features that differentiate clusters

### ✅ AI Analysis
- [ ] Identifies learning rate as most critical parameter
- [ ] Recognizes benefit of LR scheduling
- [ ] Detects overfitting in experiment 18
- [ ] Explains why combined approach (17, 19) works best
- [ ] Provides actionable recommendations

### ✅ Code Diff Analysis (if commits enabled)
- [ ] Correlates architectural changes with performance
- [ ] Identifies which code changes led to improvements
- [ ] Explains causal relationship (not just correlation)

### ✅ Recommendations
- [ ] Suggests using LR in range 0.001-0.01
- [ ] Recommends LR scheduling for best results
- [ ] Suggests regularization techniques
- [ ] Provides specific next experiments to try

---

## 🎓 Educational Value

This test suite demonstrates:

1. **Systematic experimentation** - varying one factor at a time
2. **Realistic ML workflow** - iterative improvement process
3. **Importance of hyperparameter tuning**
4. **Benefits of combining techniques**
5. **How to identify overfitting**

It's designed to be:
- **Fast** - each experiment runs in 1-3 minutes on CPU
- **Reproducible** - fixed random seeds, deterministic
- **Interpretable** - clear cause-and-effect relationships
- **Comprehensive** - covers all major training aspects

---

## 📊 Expected Runtime

| Mode | Hardware | Total Time |
|------|----------|------------|
| Sequential | CPU | ~30-40 minutes |
| Sequential | GPU | ~15-20 minutes |
| Parallel (4 workers) | CPU | ~10-15 minutes |
| Parallel (4 workers) | GPU | ~5-8 minutes |

*Note: First run downloads MNIST dataset (~50MB)*

---

## 🐛 Troubleshooting

**WandB not logging?**
```bash
wandb login
# Or set environment variable
export WANDB_API_KEY=your_key_here
```

**Out of memory?**
- Reduce batch size in configs
- Run fewer experiments in parallel
- Use `--workers 2` instead of 4

**Experiments too slow?**
- Reduce epochs in configs (change 10 → 5)
- Run in parallel: `./run_all.sh --parallel`
- Use GPU if available

**Git commits not working?**
- Ensure you're in a git repository
- Stage the config files first: `git add configs/`
- Check git config: `git config user.name` and `git config user.email`

---

## 🔬 Advanced Usage

### Custom Experiments

Create your own config file:
```json
{
  "experiment_name": "my_experiment",
  "description": "Testing XYZ hypothesis",
  "hidden_layers": [512, 256],
  "batch_size": 64,
  "learning_rate": 0.005,
  "optimizer": "adam",
  "epochs": 15,
  "dropout": 0.3,
  "batch_norm": true
}
```

Run it:
```bash
python3 train.py --config my_config.json --wandb-project my-project
```

### Extracting Results

Results are automatically logged to WandB. To extract locally:

```python
import wandb

api = wandb.Api()
runs = api.runs("YOUR_USERNAME/mnist-test-suite")

for run in runs:
    print(f"{run.name}: {run.summary['val_accuracy']:.2f}%")
```

---

## 📝 License

This test suite is provided as-is for testing Query.ai. Modify and extend as needed.

---

## 🚀 Next Steps

After running this test suite:

1. **Load data into Query.ai**
   - Point to WandB project: `mnist-test-suite`
   - Load all 20 runs

2. **Test clustering**
   - Try different numbers of clusters (3, 4, 5)
   - Verify high-performance experiments cluster together

3. **Generate AI insights**
   - Ask for analysis of best vs worst clusters
   - Verify it identifies key parameters
   - Check quality of recommendations

4. **Test code diff analysis** (if commits enabled)
   - Select two experiments with different performance
   - Verify it identifies relevant code changes
   - Check causal explanations

5. **Validate recommendations**
   - Do suggested next experiments make sense?
   - Are they specific and actionable?
   - Do they align with actual best results?

---

**Questions or issues?** This test suite is designed to be self-contained and easy to modify. Adjust configs as needed for your validation requirements!
