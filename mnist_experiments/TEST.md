# Complete Testing Guide: MNIST Test Suite + Query.ai Validation

This guide provides complete end-to-end instructions for:
1. Setting up and running the MNIST experiments
2. Installing and configuring Query.ai
3. Testing Query.ai with the MNIST data
4. Validating that Query.ai discovers expected insights

**Total Time**: ~1-2 hours (including experiment runtime)

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL recommended)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for parallel execution)
- **Storage**: 500MB free space (for MNIST data + dependencies)
- **Optional**: CUDA-compatible GPU (speeds up training 2-3x)

### Required Accounts
1. **WandB Account** (free)
   - Sign up at: https://wandb.ai/signup
   - Get API key: https://wandb.ai/settings (under "API keys")

2. **Anthropic Account** (for Query.ai AI analysis)
   - Sign up at: https://console.anthropic.com/
   - Create API key: https://console.anthropic.com/settings/keys
   - Note: Free tier includes credits for testing

### Software Requirements
```bash
# Check Python version (must be 3.8+)
python3 --version

# Check pip
pip --version

# Check git
git --version
```

---

# PART A: MNIST Experiment Setup & Execution

## Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/sergeicu/wandbai.git
cd wandbai

# Checkout the MNIST test suite branch
git checkout claude/mnist-test-suite-design-019NRdXVQtpT8bkH1qx312i9

# Navigate to experiments directory
cd mnist_experiments
```

## Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Expected packages**:
- torch>=2.0.0
- torchvision>=0.15.0
- wandb>=0.15.0
- numpy>=1.24.0

## Step 3: Configure WandB

```bash
# Login to WandB
wandb login

# Paste your API key when prompted
# Find your API key at: https://wandb.ai/settings
```

**Verify login**:
```bash
wandb whoami
# Should show: Logged in as: your_username
```

## Step 4: Verify Setup

Run the validation script:

```bash
./setup_and_test.sh
```

**Expected output**:
```
✓ Python 3.x.x
✓ Git repository detected
✓ Dependencies installed
✓ WandB authenticated as: your_username
✓ Found all 20 experiment configs
✓ Training script works
```

## Step 5: Run Experiments

You have several options:

### Option A: Quick Test (1 experiment, ~2 min)

Test that everything works:

```bash
python3 train.py \
    --config configs/00_baseline.json \
    --wandb-project mnist-test-suite \
    --wandb-run-name test-run
```

**Expected output**:
```
Using device: cpu (or cuda)
Epoch 1/10:
  Train Loss: 0.4523, Train Acc: 87.23%
  Val Loss: 0.2156, Val Acc: 93.45%
  ...
Epoch 10/10:
  Train Loss: 0.0823, Train Acc: 97.56%
  Val Loss: 0.0945, Val Acc: 97.12%
```

Check WandB dashboard:
- Go to: https://wandb.ai/YOUR_USERNAME/mnist-test-suite
- Verify the run appears with metrics

### Option B: Run All Experiments - Sequential (~30-40 min)

**Recommended for first-time users** (easier to monitor):

```bash
./run_all.sh --wandb-project mnist-test-suite
```

**Progress tracking**:
- Each experiment prints progress in real-time
- Final summary shows success/failure
- All results logged to WandB

### Option C: Run All Experiments - Parallel (~10-15 min)

**Fastest option** (requires more RAM):

```bash
./run_all.sh --parallel --workers 4 --wandb-project mnist-test-suite
```

**Notes**:
- Uses 4 parallel workers
- Reduce `--workers 2` if system struggles
- GPU users: Can handle more workers

### Option D: With Git Commits (for code diff analysis)

**Enables Query.ai code diff features**:

```bash
./run_all.sh \
    --parallel \
    --workers 4 \
    --wandb-project mnist-test-suite \
    --create-commits
```

**What this does**:
- Creates separate git commit for each experiment
- Allows Query.ai to correlate code changes with performance
- Recommended for full feature testing

### Option E: Run Specific Experiments

```bash
python3 run_experiments.py \
    --configs configs/00_baseline.json configs/17_best_combined.json \
    --wandb-project mnist-test-suite
```

## Step 6: Verify Experiments Completed

### Check Locally

```bash
# You should see summary like:
# ✓ Successful experiments:
#   - 00_baseline (commit: a3f8b2c4) (127.3s)
#   - 01_arch_deeper (commit: b4e9c5d6) (132.1s)
#   ...
# Total experiments: 20
# Successful: 20
# Failed: 0
```

### Check WandB Dashboard

1. Go to: https://wandb.ai/YOUR_USERNAME/mnist-test-suite
2. Verify 20 runs appear
3. Click on any run to see:
   - Training curves (loss, accuracy)
   - Final metrics
   - Config parameters
   - System info

**Expected metrics range**:
- Best runs: 97.5-98.5% val accuracy
- Medium runs: 96.5-97.5% val accuracy
- Poor runs: 88-96% val accuracy

---

# PART B: Query.ai Setup & Installation

## Step 1: Navigate to Query.ai Code

```bash
# From wandbai repository root
cd ..  # Go back to repository root

# Fetch the Query.ai branch
git fetch origin claude/wandb-integration-app-01MUHtVbunM86AfQESgzw7N8

# Checkout Query.ai branch
git checkout claude/wandb-integration-app-01MUHtVbunM86AfQESgzw7N8
```

## Step 2: Install Query.ai Dependencies

```bash
# If you used a virtual environment before, deactivate and create new one
# (Or use the same one if you prefer)
deactivate  # If in previous venv
python3 -m venv queryai-venv
source queryai-venv/bin/activate  # On Windows: queryai-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Key packages installed**:
- streamlit (web UI)
- anthropic (Claude API)
- wandb (experiment tracking)
- scikit-learn (clustering)
- pandas, numpy (data processing)
- gitpython (code diff analysis)

## Step 3: Configure Environment Variables

### Option A: Using .env file (Recommended)

```bash
# Create .env file
cat > .env << 'EOF'
WANDB_API_KEY=your_wandb_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF
```

Replace placeholders:
- `your_wandb_api_key_here`: Get from https://wandb.ai/settings
- `your_anthropic_api_key_here`: Get from https://console.anthropic.com/settings/keys

### Option B: Using environment variables

```bash
export WANDB_API_KEY=your_wandb_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Step 4: Verify Installation

```bash
# Test imports
python3 test_imports.py
```

**Expected output**:
```
✓ All imports successful
✓ Streamlit version: X.X.X
✓ WandB version: X.X.X
✓ Anthropic version: X.X.X
```

## Step 5: Launch Query.ai

```bash
streamlit run app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

Your browser should automatically open to http://localhost:8501

---

# PART C: Testing Query.ai with MNIST Data

## Step 1: Initial Configuration

In the Query.ai web interface:

### 1. Authentication (if enabled)
- Default: No auth required
- If prompted, check `auth.py` for credentials

### 2. Configure API Keys

In the sidebar, enter:

**WandB Configuration**:
- **WandB API Key**: Your key from https://wandb.ai/settings
- **Entity**: Your WandB username (e.g., "john_doe")
- **Project**: `mnist-test-suite`

**Anthropic API Key** (for AI analysis):
- Your key from https://console.anthropic.com/settings/keys

Click **"Save Configuration"** or proceed to next step (depending on UI)

## Step 2: Load Experiments

1. Click **"Load Experiments"** button

**Expected behavior**:
- Loading spinner appears
- Progress bar (if implemented)
- After 5-10 seconds, you should see:
  - "✓ Loaded 20 runs from mnist-test-suite"
  - Summary stats: Total runs, Completed, Running, Failed

**Data displayed**:
- Run names (00_baseline, 01_arch_deeper, etc.)
- Final metrics (accuracy, loss)
- Config parameters (learning_rate, optimizer, etc.)
- Timestamps

### Troubleshooting Load Issues

**If no runs appear**:
```bash
# Verify runs exist in WandB
wandb status
wandb runs --project mnist-test-suite
```

**If API errors**:
- Check API key is correct
- Verify entity name matches your WandB username
- Check project name is exactly `mnist-test-suite`

## Step 3: Cluster Experiments

### 3.1 Set Clustering Parameters

In the sidebar:
- **Number of Clusters**: Start with `4`
- **Clustering Algorithm**: `K-Means` (default)

### 3.2 Run Clustering

1. Click **"Analyze & Cluster"** button

**Expected output**:
- Processing spinner
- After 1-3 seconds:
  - "✓ Clustered 20 experiments into 4 groups"
  - Cluster summary appears

### 3.3 Review Cluster Summary

You should see 4 clusters with approximately:

**Cluster 0 (High Performance)**:
- Size: 4-5 experiments
- Avg accuracy: ~98.0%
- Members: 17_best_combined, 19_optimal_tuned, 13_scheduler_step, etc.

**Cluster 1 (Good Performance)**:
- Size: 9-11 experiments
- Avg accuracy: ~97.0%
- Members: 00_baseline, 02_arch_wider, 03_arch_dropout, etc.

**Cluster 2 (Suboptimal)**:
- Size: 3-4 experiments
- Avg accuracy: ~92.0%
- Members: 05_lr_very_low, 07_lr_high, etc.

**Cluster 3 (Overfitting)**:
- Size: 1-2 experiments
- Avg train acc: ~98.5%, val acc: ~95.8%
- Members: 18_overfit_scenario

## Step 4: Explore Individual Experiments

### 4.1 Select an Experiment

Click on any experiment (e.g., "17_best_combined")

**Expected view**:

**Experiment Details**:
- Name: 17_best_combined
- Status: Finished
- Duration: ~XXX seconds
- Final metrics:
  - train_accuracy: 98.3%
  - val_accuracy: 98.1%
  - final_loss: 0.065

**Configuration**:
```json
{
  "learning_rate": 0.01,
  "batch_size": 128,
  "optimizer": "adam",
  "hidden_layers": [256, 128],
  "dropout": 0.2,
  "batch_norm": true,
  "lr_scheduler": true,
  "scheduler_type": "cosine"
}
```

**Training Curves** (if visualization enabled):
- Loss curve showing smooth convergence
- Accuracy curve reaching 98%+

### 4.2 Compare to Baseline

Open "00_baseline" in another tab (or switch):

**Differences**:
- Baseline: 97.0% val acc
- Best combined: 98.1% val acc
- Improvement: +1.1%

**Config differences**:
- Baseline: No dropout, no batch norm, no LR scheduler, smaller network
- Best: All optimizations enabled

## Step 5: Generate AI Insights

### 5.1 For High-Performance Cluster

1. Select an experiment from Cluster 0 (e.g., "17_best_combined")
2. Click **"Generate AI Insights"** button

**Expected AI response** (within 5-10 seconds):

```
Summary:
This experiment achieves top-tier performance (98.1% validation accuracy)
by combining multiple optimization techniques: wider architecture, batch
normalization, dropout regularization, and cosine annealing LR scheduling.

Key Insights:
• LR scheduling (cosine) enables smooth convergence and 0.5-1% accuracy boost
• Batch normalization stabilizes training, allowing higher initial LR (0.01)
• Dropout (0.2) prevents overfitting while maintaining high performance
• Wider layers (256/128 vs 128/64) increase model capacity by 2x
• Combined optimizations show synergistic effects (+1.1% vs baseline)

Recommendations:
• This configuration represents best practices for MNIST
• Consider testing dropout values 0.15-0.30 to fine-tune
• Try increasing to 3 hidden layers [256, 128, 64] for potential gains
• Experiment with learning_rate=0.005 (between baseline 0.001 and this 0.01)
• Apply this template to similar image classification tasks

Comparison to Other Clusters:
• Outperforms Cluster 1 (baseline) by +1.1% through combined optimizations
• Avoids overfitting seen in Cluster 3 through dropout+batch norm
• More stable than Cluster 2 experiments with poor LR choices
```

### 5.2 For Overfitting Experiment

1. Select "18_overfit_scenario"
2. Click **"Generate AI Insights"**

**Expected AI response**:

```
Summary:
This experiment shows clear overfitting: 98.5% train accuracy but only
95.8% validation accuracy (gap: 2.7%). The very deep network (5 layers)
lacks regularization, causing it to memorize training data.

Key Insights:
• Train/val accuracy gap of 2.7% indicates overfitting
• Model has high capacity (5 layers: 512+512+256+256+128 neurons)
• No regularization: dropout=0, batch_norm=false, weight_decay=0
• Small batch size (32) allows easier memorization
• Validation loss plateaus while training loss continues decreasing

Root Causes:
• Excessive model depth for MNIST complexity
• No dropout to prevent co-adaptation
• No L2 regularization to constrain weights
• Long training (20 epochs) without early stopping

Recommendations:
• Add dropout=0.25 to all hidden layers (expected +2% val accuracy)
• Enable batch normalization for implicit regularization
• Reduce depth to 2-3 layers (current: 5)
• Add weight_decay=0.0001 for L2 regularization
• Implement early stopping with patience=3
• Increase batch_size to 128

Expected Impact:
Implementing these changes should close the 2.7% train/val gap and
achieve ~97.5-98% validation accuracy.
```

### 5.3 For Poor Performance Experiment

1. Select "07_lr_high" (learning_rate=0.1)
2. Click **"Generate AI Insights"**

**Expected AI response**:

```
Summary:
This experiment performs poorly (~88% validation accuracy) due to
excessively high learning rate (0.1) causing training instability.

Key Insights:
• Learning rate 0.1 is 10-100x higher than optimal range (0.001-0.01)
• Training loss shows high variance and instability
• Model overshoots minima repeatedly, preventing convergence
• Final loss (0.45) is 5x higher than top performers (0.08)

Evidence of Instability:
• Loss spikes throughout training
• Accuracy plateaus early and fluctuates
• Gradient updates are too large for fine optimization

Comparison to Similar Experiments:
• Baseline (LR=0.001): 97.0% accuracy, stable training
• Medium LR (LR=0.01): 97.5% accuracy, faster convergence
• High LR (LR=0.1): 88% accuracy, unstable training

Recommendations:
• Reduce learning rate to 0.001-0.01 range (expected +8-10% accuracy)
• If faster training desired, use LR=0.01 with scheduler
• Consider gradient clipping if still unstable
• Monitor loss variance as indicator of LR appropriateness

Key Lesson:
Learning rate is the most critical hyperparameter. Too high causes
instability, too low causes slow convergence. MNIST sweet spot: 0.001-0.01.
```

## Step 6: Test Code Diff Analysis (if commits enabled)

**Only if you ran with `--create-commits`**:

### 6.1 Select Two Experiments with Different Performance

- Experiment A: "00_baseline" (97.0% acc)
- Experiment B: "04_arch_batchnorm" (97.5% acc)

### 6.2 View Code Diff

Click **"View Code Changes"** or **"Compare with Previous"**

**Expected diff display**:

```diff
diff --git a/configs/00_baseline.json b/configs/04_arch_batchnorm.json
--- a/configs/00_baseline.json
+++ b/configs/04_arch_batchnorm.json
@@ -1,5 +1,5 @@
 {
-  "experiment_name": "00_baseline",
+  "experiment_name": "04_arch_batchnorm",
-  "batch_norm": false,
+  "batch_norm": true,
 }
```

### 6.3 AI Analysis of Code Changes

**Expected AI correlation**:

```
Code Change Impact Analysis:

Change: Added batch_norm=true
Impact: +0.5% validation accuracy (97.0% → 97.5%)

Explanation:
Batch normalization was added to the network architecture. This change
normalizes layer inputs during training, which:
• Stabilizes gradient flow
• Allows higher learning rates
• Acts as regularization
• Reduces internal covariate shift

Performance Impact:
• Validation accuracy: +0.5%
• Training stability: Improved (lower loss variance)
• Convergence speed: Slightly faster (reaches 97% by epoch 6 vs 7)

Why This Worked:
Without batch norm, the network's internal distributions shift as weights
update, making optimization harder. Batch norm stabilizes this, allowing
more efficient learning and better generalization.

Recommendation:
Batch normalization is a low-cost, high-impact addition for most neural
networks. Consider combining with dropout for even better results.
```

## Step 7: Test Clustering with Different Parameters

### 7.1 Try 3 Clusters

Change clustering parameter to k=3, re-run clustering

**Expected clusters**:
1. High performers (98%+): 4-5 experiments
2. Medium performers (95-97.5%): 12-14 experiments
3. Low performers (<95%): 2-3 experiments

### 7.2 Try 5 Clusters

Change to k=5, re-run

**Expected clusters**:
1. Best (98%+): LR scheduler experiments
2. Good (97-97.5%): Single optimizations
3. Baseline (96.5-97%): Reasonable configs
4. Poor (<95%): Bad LR choices
5. Overfitting: Train/val gap

**Validate**: Query.ai should provide meaningful labels for each cluster

---

# PART D: What Query.ai Should Discover

## ✅ Core Functionality Validation

### 1. Data Loading & Extraction

**Query.ai must successfully**:
- [ ] Fetch all 20 runs from WandB
- [ ] Extract metrics: train_loss, train_accuracy, val_loss, val_accuracy, learning_rate
- [ ] Extract configs: learning_rate, batch_size, optimizer, hidden_layers, dropout, batch_norm, etc.
- [ ] Handle metadata: run name, state, duration, timestamps
- [ ] Extract git commit hashes (if commits enabled)

**Validation**:
```python
# You should be able to see these in Query.ai UI or verify programmatically:
assert len(runs) == 20
assert all('val_accuracy' in run.summary for run in runs)
assert all('config_learning_rate' in run for run in runs)
```

### 2. Clustering Accuracy

**Query.ai must cluster experiments into meaningful groups**:

#### Test: K=4 Clustering

**Cluster 0: High Performance**
- [ ] Contains experiments: 17, 19, 13, 14 (possibly 04)
- [ ] Mean val_accuracy: 97.5-98.5%
- [ ] Common feature: lr_scheduler=true in 80%+ of members
- [ ] Auto-label includes: "High accuracy" or "Best performance"

**Cluster 1: Good Performance**
- [ ] Contains: 00, 02, 03, 06, 08, 09, 10, 12, 15, 16
- [ ] Mean val_accuracy: 96.5-97.5%
- [ ] Diverse configs, but reasonable hyperparameters
- [ ] Auto-label: "Baseline" or "Good performance"

**Cluster 2: Suboptimal**
- [ ] Contains: 05, 07 (possibly 11, 01)
- [ ] Mean val_accuracy: 88-96%
- [ ] Common issue: LR too high (0.1) or too low (0.0001)
- [ ] Auto-label includes: "Low accuracy" or "Convergence issues"

**Cluster 3: Overfitting**
- [ ] Contains: 18
- [ ] High train_accuracy (98%+), lower val_accuracy (~96%)
- [ ] Train/val gap: 2-3%
- [ ] Auto-label mentions: "Overfitting" or train/val discrepancy

#### Feature Importance Detection

Query.ai should identify these as most discriminative features:

1. **Learning rate** (highest impact)
   - [ ] Detects LR range 0.001-0.01 in best clusters
   - [ ] Identifies LR=0.1 in poor cluster
   - [ ] Identifies LR=0.0001 in slow-convergence cluster

2. **LR scheduler** (high impact)
   - [ ] Recognizes lr_scheduler=true in top cluster
   - [ ] Quantifies impact: ~0.5-1% accuracy boost

3. **Regularization** (medium impact)
   - [ ] Notes dropout, batch_norm, weight_decay presence
   - [ ] Correlates with generalization (smaller train/val gap)

4. **Architecture** (low-medium impact)
   - [ ] Wider networks slightly better than deeper
   - [ ] Detects overfitting risk in very deep networks

### 3. AI Analysis Quality

**For each cluster, AI analysis must provide**:

#### Summary (1-2 sentences)
- [ ] Accurate description of cluster performance
- [ ] Identifies key defining characteristics
- [ ] Mentions number of experiments

Example:
> "This cluster contains 5 experiments achieving 98%+ validation accuracy. All use learning rate scheduling combined with regularization techniques."

#### Insights (3-5 bullet points)
- [ ] Identifies common config patterns
- [ ] Explains why these configs work
- [ ] Compares to other clusters
- [ ] Mentions training dynamics (stability, convergence)

Example insights:
- [ ] "All experiments use LR scheduling (step, cosine, or reduce-on-plateau)"
- [ ] "80% include batch normalization or dropout for regularization"
- [ ] "Learning rates start higher (0.005-0.01) but decay during training"
- [ ] "Training shows smooth convergence with low loss variance"

#### Recommendations (2-4 actionable items)
- [ ] Specific, actionable next experiments
- [ ] Concrete parameter values suggested
- [ ] Explains expected impact
- [ ] Prioritized by likely improvement

Example recommendations:
- [ ] "Try dropout=0.3 (current best is 0.2) for potential +0.2% gain"
- [ ] "Combine batch_norm + dropout in baseline to match top cluster performance"
- [ ] "Experiment with learning_rate=0.005 (between 0.001 and 0.01)"

#### Key Findings (2-4 discoveries)
- [ ] Explains causal relationships (not just correlations)
- [ ] Identifies unexpected patterns
- [ ] Quantifies performance differences

Example findings:
- [ ] "LR scheduling adds +0.8% accuracy on average across all architectures"
- [ ] "Wider networks (256/128) outperform deeper (4-layer) by +0.5%"
- [ ] "All sub-95% accuracy experiments have LR outside 0.001-0.01 range"

### 4. Cross-Experiment Insights

**Query.ai should identify these key patterns across all 20 experiments**:

#### Learning Rate Impact (Most Critical)
- [ ] LR=0.001-0.01 → Good performance (96.5-98%)
- [ ] LR=0.0001 → Under-training, slow convergence (~92%)
- [ ] LR=0.1 → Instability, poor convergence (~88%)
- [ ] Impact magnitude: 5-10% accuracy variation

**Validation statement**:
> "Learning rate is the most critical hyperparameter, with a sweet spot of 0.001-0.01 for MNIST. Values outside this range cause 5-10% accuracy degradation."

#### LR Scheduling (High Impact)
- [ ] All 98%+ experiments use LR scheduling
- [ ] Baseline → Add scheduler: +0.5-1% accuracy
- [ ] Works with step, cosine, and reduce-on-plateau

**Validation statement**:
> "LR scheduling is the key differentiator between good (97%) and excellent (98%+) performance. All top-4 experiments use scheduling."

#### Regularization (Medium Impact)
- [ ] Dropout adds ~0.3-0.5% accuracy
- [ ] Batch norm adds ~0.3-0.5% accuracy
- [ ] Prevents overfitting (reduces train/val gap)
- [ ] Combined: +0.5-1% with better generalization

**Validation statement**:
> "Regularization techniques (dropout, batch norm, L2) each add 0.3-0.5% accuracy and are essential for preventing overfitting."

#### Architecture (Low-Medium Impact)
- [ ] Wider (256/128) beats deeper (4 layers) by ~0.3%
- [ ] Excessive depth (5 layers) risks overfitting
- [ ] Impact: +0.3-0.5% for optimal width

**Validation statement**:
> "For MNIST, wider networks (256/128 neurons) outperform deeper architectures. Excessive depth increases overfitting risk without accuracy gains."

#### Optimizer (Low Impact)
- [ ] Adam, SGD, RMSprop perform similarly when LR tuned
- [ ] SGD needs higher LR (0.01 vs 0.001 for Adam)
- [ ] Impact: <0.5% variation

**Validation statement**:
> "Optimizer choice has minimal impact (~0.5%) when learning rate is properly tuned for each optimizer."

#### Batch Size (Low Impact)
- [ ] 32-512 range: minimal final accuracy difference
- [ ] Smaller batches: slower but more stable
- [ ] Larger batches: faster but may need LR adjustment
- [ ] Impact: <0.3% on final accuracy

**Validation statement**:
> "Batch size has minimal impact on final accuracy (32-512 range), affecting primarily training speed and stability."

### 5. Code Diff Analysis (if commits enabled)

**Query.ai must correlate code changes with performance**:

#### Example: Baseline → Best Combined

**Code changes**:
```diff
- "hidden_layers": [128, 64]
+ "hidden_layers": [256, 128]
- "batch_norm": false
+ "batch_norm": true
- "dropout": 0.0
+ "dropout": 0.2
- "lr_scheduler": false
+ "lr_scheduler": true
+ "scheduler_type": "cosine"
```

**Expected AI analysis**:
- [ ] Lists all changes detected
- [ ] Quantifies performance delta: +1.3% (97.0% → 98.3%)
- [ ] Attributes impact to each change:
  - Wider network: +0.3%
  - Batch norm: +0.3%
  - Dropout: +0.2%
  - LR scheduler: +0.5%
- [ ] Explains why each change helped
- [ ] Notes synergistic effects

**Validation statement**:
> "Four key changes led to +1.3% improvement: wider layers (+0.3%), batch norm (+0.3%), dropout (+0.2%), and LR scheduling (+0.5%). The combined effect shows these optimizations work synergistically."

#### Example: Baseline → Overfitting

**Code changes**:
```diff
- "hidden_layers": [128, 64]
+ "hidden_layers": [512, 512, 256, 256, 128]
- "batch_size": 128
+ "batch_size": 32
- "epochs": 10
+ "epochs": 20
```

**Expected AI analysis**:
- [ ] Identifies increased model capacity (5 layers, 1408 total neurons)
- [ ] Notes removal of regularization
- [ ] Connects changes to overfitting: 98.5% train, 95.8% val
- [ ] Explains causal mechanism
- [ ] Recommends specific fixes

**Validation statement**:
> "Increasing depth to 5 layers without regularization led to overfitting (2.7% train/val gap). The high capacity network memorizes training data. Adding dropout=0.25 would close this gap."

### 6. Progression Analysis

**Query.ai should detect optimization trajectory**:

- [ ] Identifies baseline: 00_baseline (97.0%)
- [ ] Tracks improvements:
  - +0.5%: Add batch norm (04)
  - +0.5%: Add LR scheduler (13, 14)
  - +1.3%: Combine all (17, 19)
- [ ] Shows diminishing returns
- [ ] Suggests next experiments

**Validation statement**:
> "Progression from baseline (97.0%) to optimal (98.3%) shows cumulative +1.3% gain through systematic addition of batch norm, dropout, wider architecture, and LR scheduling. Each optimization adds 0.2-0.5%."

### 7. Hypothesis Generation

**Query.ai should suggest novel experiments not in the suite**:

Examples of good suggestions:
- [ ] "Try 3-layer network [256, 128, 64] - interpolates between best configs"
- [ ] "Test learning_rate=0.005 with cosine scheduler - between best values"
- [ ] "Combine SGD optimizer with LR scheduling - untested combination"
- [ ] "Try dropout=0.3 (current best is 0.25) for potential +0.2% gain"
- [ ] "Ensemble experiments 17 and 19 for potential +0.3-0.5% boost"

**Quality criteria**:
- [ ] Specific parameter values (not vague)
- [ ] Builds on successful experiments
- [ ] Tests reasonable hypotheses
- [ ] Explains expected outcome
- [ ] Estimates impact magnitude

---

## 📊 Quantitative Validation Metrics

### Clustering Quality Metrics

**Silhouette Score** (measures cluster separation):
- [ ] Score > 0.3: Decent clustering
- [ ] Score > 0.5: Good clustering
- [ ] Top cluster members have high intra-cluster similarity

**Cluster Purity** (are similar experiments together?):
- [ ] High-performance experiments (97.5%+) in same cluster: >80%
- [ ] Low-performance experiments (<95%) in same cluster: >70%
- [ ] Overfitting experiment isolated or in small cluster

### AI Analysis Accuracy

**Factual Correctness**:
- [ ] Quoted metrics match actual values (±0.2%)
- [ ] Config parameters mentioned are accurate
- [ ] Performance rankings are correct
- [ ] No hallucinated experiments or metrics

**Insight Relevance**:
- [ ] >80% of insights are actionable
- [ ] >90% of insights are factually correct
- [ ] >70% of recommendations are reasonable next steps

**Causal Reasoning Quality**:
- [ ] Distinguishes correlation from causation
- [ ] Explains mechanisms, not just patterns
- [ ] Identifies confounding factors where relevant

### Response Time (Performance)

- [ ] Data loading: <10 seconds for 20 runs
- [ ] Clustering: <5 seconds
- [ ] AI analysis generation: <10 seconds per cluster
- [ ] Total workflow (load → cluster → analyze): <30 seconds

---

## 🎯 Success Criteria Summary

### Minimum Passing Grade (MVP Validation)

Query.ai successfully:
- [x] Loads all 20 MNIST experiments with complete data
- [x] Clusters into 3-4 meaningful groups (high/medium/low performance)
- [x] Identifies learning rate as critical parameter
- [x] Detects overfitting in experiment 18
- [x] Generates insights for each cluster with >70% relevance
- [x] Provides at least 2 actionable recommendations per cluster

### Good Performance

All MVP criteria, plus:
- [x] Identifies LR scheduling as key to top performance
- [x] Correctly ranks parameter importance (LR > scheduling > regularization > architecture)
- [x] Explains causal mechanisms (not just correlations)
- [x] Code diff analysis correlates changes with performance (if enabled)
- [x] Suggests 3+ reasonable novel experiments
- [x] Cluster labels are meaningful and accurate

### Excellent Performance

All Good criteria, plus:
- [x] Quantifies impact of each optimization (+X% accuracy)
- [x] Detects synergistic effects in combined experiments
- [x] Identifies progression path from baseline to optimal
- [x] Explains why certain configs fail (not just that they fail)
- [x] Provides experiment-specific, tailored recommendations
- [x] Generates hypotheses for beating current best (98.5%+)
- [x] Cluster statistics accurately characterize each group
- [x] AI analysis reads like expert ML researcher insights

---

## 🔍 Example Validation Workflow

### Complete Test Script

```bash
# 1. Verify data loading
echo "Test 1: Data Loading"
# In Query.ai UI:
# - Load mnist-test-suite project
# - Check: 20 runs loaded
# - Check: All metrics present (val_accuracy, train_accuracy, etc.)
# ✓ PASS if all 20 runs with complete data

# 2. Test clustering
echo "Test 2: Clustering"
# - Set k=4
# - Click "Analyze & Cluster"
# - Check: 4 clusters created
# - Check: Cluster 0 has ~4-5 experiments with val_acc > 97.5%
# - Check: Cluster 2-3 has experiments with val_acc < 95%
# ✓ PASS if meaningful separation

# 3. Test AI insights (high-performance cluster)
echo "Test 3: AI Insights - High Performance"
# - Select experiment 17_best_combined
# - Click "Generate AI Insights"
# - Check: Mentions LR scheduling
# - Check: Identifies combined optimizations
# - Check: Provides specific recommendations
# ✓ PASS if insights are relevant and actionable

# 4. Test AI insights (overfitting)
echo "Test 4: AI Insights - Overfitting Detection"
# - Select experiment 18_overfit_scenario
# - Click "Generate AI Insights"
# - Check: Identifies overfitting (train/val gap)
# - Check: Suggests regularization
# - Check: Explains causal mechanism
# ✓ PASS if overfitting detected and explained

# 5. Test AI insights (poor performance)
echo "Test 5: AI Insights - Poor Performance"
# - Select experiment 07_lr_high
# - Click "Generate AI Insights"
# - Check: Identifies high LR as problem
# - Check: Suggests reducing LR
# - Check: Quantifies expected improvement
# ✓ PASS if root cause identified

# 6. Test code diff analysis (if enabled)
echo "Test 6: Code Diff Analysis"
# - Select two experiments with different performance
# - View code diff
# - Check: Diff shows config changes
# - Check: AI correlates changes with performance
# ✓ PASS if changes correlated with metrics

# 7. Test cross-cluster insights
echo "Test 7: Cross-Cluster Analysis"
# - Generate insights for all 4 clusters
# - Check: Identifies LR as most important parameter
# - Check: Recognizes LR scheduling pattern
# - Check: Quantifies optimization progression
# ✓ PASS if global patterns identified

echo "All tests complete!"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. MNIST Experiments Won't Run

**Error**: `ModuleNotFoundError: No module named 'torch'`
```bash
pip install -r requirements.txt
```

**Error**: `wandb.errors.AuthenticationError`
```bash
wandb login
# Paste your API key from https://wandb.ai/settings
```

**Error**: Experiments fail with CUDA errors
```bash
# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
```

#### 2. Query.ai Won't Load Experiments

**Error**: "No runs found"
- Check project name is exactly `mnist-test-suite`
- Verify experiments completed and uploaded to WandB
- Check WandB entity matches your username

**Error**: API key invalid
- Get new key from https://wandb.ai/settings
- Ensure no extra spaces when pasting

#### 3. Clustering Doesn't Make Sense

**Issue**: All experiments in one cluster
- Check that experiments have varied performance (88-98%)
- Try different k values (3, 4, 5)
- Verify metrics were logged correctly

**Issue**: Clusters seem random
- Check clustering algorithm (K-Means recommended)
- Increase number of clusters
- Verify enough variation in experiment configs

#### 4. AI Analysis is Generic/Unhelpful

**Issue**: Vague insights
- Ensure Anthropic API key is valid
- Check that experiment data includes configs
- Try different experiments (compare best vs worst)

**Issue**: Factually incorrect
- Verify data loaded correctly
- Check for NaN values in metrics
- Report as bug if persists

#### 5. Code Diff Not Working

**Issue**: "No commit hash found"
- Ensure you ran with `--create-commits` flag
- Check git repository is initialized
- Verify commits were created (run `git log`)

**Issue**: Diff shows no changes
- Each experiment should have unique config
- Commits may have been squashed
- Try re-running experiments with fresh commits

### Performance Issues

**Experiments too slow**:
```bash
# Reduce epochs for testing
# Edit configs/*.json: "epochs": 5  # Instead of 10-20

# Use smaller network
# Edit configs: "hidden_layers": [64, 32]  # Instead of [256, 128]
```

**Query.ai UI slow**:
```bash
# Reduce number of experiments
python3 run_experiments.py --configs configs/00_baseline.json configs/17_best_combined.json configs/18_overfit_scenario.json

# Or sample runs in Query.ai (if feature available)
```

### Getting Help

1. **Check logs**:
   ```bash
   # MNIST experiments
   cat wandb/debug.log

   # Query.ai
   streamlit run app.py --server.headless=true  # Shows more verbose output
   ```

2. **Verify setup**:
   ```bash
   cd mnist_experiments
   ./setup_and_test.sh
   ```

3. **Test minimal case**:
   ```bash
   # Just run baseline
   python3 train.py --config configs/00_baseline.json --wandb-project test

   # Load in Query.ai
   # If this works, problem is with specific experiments
   ```

---

## 📚 Additional Resources

### Documentation
- **MNIST Suite**: `/mnist_experiments/README.md`
- **Expected Clusters**: `/mnist_experiments/EXPECTED_CLUSTERS.md`
- **Query.ai How It Works**: `/HOW_IT_WORKS.md` (on Query.ai branch)
- **Query.ai Quickstart**: `/QUICKSTART.md` (on Query.ai branch)

### External Resources
- **WandB Docs**: https://docs.wandb.ai/
- **Anthropic API**: https://docs.anthropic.com/
- **PyTorch Tutorials**: https://pytorch.org/tutorials/

### Community
- **Issues**: https://github.com/sergeicu/wandbai/issues
- **WandB Forum**: https://community.wandb.ai/

---

## ✅ Final Checklist

Before concluding testing, verify:

### MNIST Experiments
- [ ] All 20 experiments completed successfully
- [ ] Results visible on WandB dashboard
- [ ] Performance range: 88-98.5% as expected
- [ ] Git commits created (if using code diff feature)

### Query.ai Setup
- [ ] Application launches without errors
- [ ] API keys configured correctly
- [ ] UI loads in browser

### Core Functionality
- [ ] Loads 20 runs from WandB
- [ ] Clustering produces 3-4 meaningful groups
- [ ] AI analysis generates insights
- [ ] Recommendations are specific and actionable

### Validation
- [ ] Identifies LR as critical parameter
- [ ] Detects LR scheduling in top performers
- [ ] Recognizes overfitting in experiment 18
- [ ] Explains causal relationships
- [ ] Suggests reasonable next experiments

### Optional (Code Diff)
- [ ] Displays code differences between experiments
- [ ] Correlates changes with performance
- [ ] AI explains impact of changes

---

## 🎉 Conclusion

If all validation criteria pass, Query.ai successfully:

1. ✅ Integrates with WandB and loads experiment data
2. ✅ Clusters experiments intelligently
3. ✅ Generates AI insights using Claude
4. ✅ Identifies key performance factors
5. ✅ Provides actionable recommendations
6. ✅ Understands causal relationships
7. ✅ Helps researchers optimize their ML workflows

**Next Steps**:
- Test with real research projects
- Expand to other datasets/domains
- Iterate on AI prompt engineering
- Add advanced features (literature review, auto-experimentation)

**Congratulations!** 🎊 You've successfully validated Query.ai with a comprehensive MNIST test suite.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Tested With**: Python 3.8+, PyTorch 2.0+, WandB 0.15+, Streamlit 1.x
