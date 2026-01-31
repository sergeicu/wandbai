# Expected Clustering Results for Query.ai

This document outlines what clustering patterns Query.ai should discover when analyzing the 20 MNIST experiments.

## 🎯 Optimal Clustering: 4 Clusters

When using K-Means with k=4, Query.ai should discover these clusters:

---

## Cluster 1: 🏆 High Performance (Top Performers)

**Size**: 4-5 experiments
**Avg Val Accuracy**: 97.8-98.5%
**Avg Val Loss**: 0.05-0.10

### Members:
- `17_best_combined` (98.0-98.5%)
- `19_optimal_tuned` (98.0-98.5%)
- `13_scheduler_step` (97.5-98.0%)
- `14_scheduler_cosine` (97.5-98.0%)
- `04_arch_batchnorm` (97.5-98.0%)

### Common Characteristics:
```json
{
  "learning_rate": 0.005-0.01,
  "lr_scheduler": true,
  "batch_norm": true (or dropout > 0),
  "optimizer": "adam",
  "batch_size": 64-128
}
```

### What Query.ai Should Say:

> **Cluster Summary**: High-performance experiments achieving 98%+ validation accuracy. These runs consistently use learning rate scheduling combined with regularization techniques.
>
> **Key Insights**:
> - All experiments use LR scheduling (step, cosine, or reduce-on-plateau)
> - 80% include batch normalization or dropout
> - Learning rates start higher (0.005-0.01) but decay during training
> - Training is stable with smooth convergence curves
>
> **Recommendations**:
> - This cluster represents best practices for MNIST
> - Consider using these configurations as templates for new tasks
> - Key combination: LR scheduling + regularization + moderate initial LR

---

## Cluster 2: ✅ Good Performance (Solid Baseline)

**Size**: 9-11 experiments
**Avg Val Accuracy**: 96.5-97.5%
**Avg Val Loss**: 0.10-0.15

### Members:
- `00_baseline` (97.0%)
- `02_arch_wider` (97.3%)
- `03_arch_dropout` (97.2%)
- `06_lr_medium` (97.0%)
- `08_opt_sgd` (96.8%)
- `09_opt_rmsprop` (97.0%)
- `10_batch_small` (97.0%)
- `12_reg_l2` (97.2%)
- `15_data_augmentation` (97.0%)
- `16_early_stopping` (97.0%)
- `01_arch_deeper` (96.5-97.0%)

### Common Characteristics:
```json
{
  "learning_rate": 0.001-0.01,
  "lr_scheduler": false (mostly),
  "optimizer": "adam" or "sgd" or "rmsprop",
  "batch_size": 32-512 (varied)
}
```

### What Query.ai Should Say:

> **Cluster Summary**: Solid baseline performance with reasonable hyperparameters. These experiments achieve good results but lack optimization techniques that push to 98%+.
>
> **Key Insights**:
> - Learning rates in the sweet spot (0.001-0.01)
> - Diverse architectural choices (depth, width, dropout)
> - No clear performance difference between optimizers at this level
> - Batch size has minimal impact in this range
>
> **What separates this from Cluster 1?**
> - Missing LR scheduling (most important differentiator)
> - Single optimization technique vs. combined approach
> - Static LR prevents reaching final 1% performance boost
>
> **Recommendations**:
> - Add LR scheduling to push these to 98%+
> - Combine regularization techniques (e.g., dropout + batch norm)
> - These configs are good starting points for iteration

---

## Cluster 3: ⚠️ Suboptimal Performance (Needs Tuning)

**Size**: 3-4 experiments
**Avg Val Accuracy**: 88-96%
**Avg Val Loss**: 0.15-0.50

### Members:
- `05_lr_very_low` (~92% - under-trained)
- `07_lr_high` (~88% - unstable training)
- `11_batch_large` (~96% - needs LR adjustment)

### Common Characteristics:
```json
{
  "learning_rate": 0.0001 (too low) or 0.1 (too high),
  "epochs": 10 (insufficient for slow LR),
  "batch_size": 512 (for one experiment)
}
```

### What Query.ai Should Say:

> **Cluster Summary**: Experiments with suboptimal hyperparameters leading to convergence issues. Clear signs of under-training or training instability.
>
> **Key Insights**:
> - LR=0.0001: Loss still decreasing at epoch 10, needs more training
> - LR=0.1: High loss variance, overshooting minima
> - Large batch (512) may need higher LR or warmup
>
> **Specific Issues**:
> - `05_lr_very_low`: Final loss ~0.25 (vs 0.08 for good runs)
> - `07_lr_high`: Loss spikes and instability throughout training
> - `11_batch_large`: Fast epochs but suboptimal convergence
>
> **Recommendations**:
> - For `05_lr_very_low`: Increase LR to 0.001 OR train for 20+ epochs
> - For `07_lr_high`: Decrease LR to 0.001-0.01 range
> - For `11_batch_large`: Use LR warmup or reduce to batch_size=128
>
> **Key Lesson**: Learning rate is the most critical hyperparameter

---

## Cluster 4: 📊 Overfitting Case (Train/Val Gap)

**Size**: 1-2 experiments
**Avg Train Accuracy**: 98-99%
**Avg Val Accuracy**: 95-96%
**Train/Val Gap**: 2-3%

### Members:
- `18_overfit_scenario` (train: 98.5%, val: 95.8%)

### Common Characteristics:
```json
{
  "hidden_layers": [512, 512, 256, 256, 128] (very deep),
  "batch_size": 32 (small),
  "dropout": 0.0 (no regularization),
  "batch_norm": false,
  "weight_decay": 0.0,
  "epochs": 20 (long training)
}
```

### What Query.ai Should Say:

> **Cluster Summary**: Clear overfitting pattern. Model memorizes training data but fails to generalize. High training accuracy with significantly lower validation accuracy.
>
> **Key Insights**:
> - Train accuracy: 98.5% but val accuracy: 95.8% (gap: 2.7%)
> - Very deep network (5 layers) without regularization
> - Training loss continues to decrease while val loss plateaus/increases
> - Classic overfitting signature
>
> **Why overfitting occurred**:
> - Model capacity (512+512+256+256+128 = very high parameter count)
> - No dropout, no batch norm, no L2 regularization
> - Small batch size (32) allows memorization
> - Long training (20 epochs) without early stopping
>
> **Recommendations**:
> - Add dropout (0.2-0.3) to all hidden layers
> - Use batch normalization for regularization
> - Add L2 regularization (weight_decay=0.0001)
> - Implement early stopping (patience=3-5)
> - Reduce model depth to 2-3 layers
> - Consider increasing batch size to 128
>
> **Key Lesson**: Regularization is essential for deep networks

---

## 🔍 Cross-Cluster Insights

### Parameter Impact Rankings (Query.ai should identify)

1. **Learning Rate** (Highest Impact)
   - Sweet spot: 0.001-0.01
   - Too low (0.0001): Poor performance cluster
   - Too high (0.1): Poor performance cluster
   - **Impact on accuracy**: 5-10% variation

2. **LR Scheduling** (High Impact)
   - Differentiates high-performance (Cluster 1) from good (Cluster 2)
   - **Impact on accuracy**: +0.5-1.0%

3. **Regularization** (Medium Impact)
   - Essential to prevent overfitting (Cluster 4 vs others)
   - Batch norm, dropout, L2 each add ~0.3-0.5%
   - **Impact on accuracy**: +0.5-1.0% combined

4. **Architecture** (Low-Medium Impact)
   - Wider > Deeper for MNIST
   - 256/128 neurons slightly better than 128/64
   - **Impact on accuracy**: +0.3-0.5%

5. **Optimizer** (Low Impact)
   - Adam, SGD, RMSprop perform similarly when LR is tuned
   - **Impact on accuracy**: <0.5% variation

6. **Batch Size** (Low Impact)
   - 32-512 range: minimal impact if LR adjusted
   - **Impact on accuracy**: <0.3% variation

---

## 📈 Expected Cluster Statistics

When Query.ai calculates cluster statistics, it should see:

### Cluster 1 (High Performance)
```
accuracy: mean=98.1%, std=0.3%, min=97.5%, max=98.5%
val_loss: mean=0.065, std=0.020, min=0.045, max=0.095
learning_rate: mean=0.007, std=0.003
lr_scheduler: 100% (all use scheduling)
batch_norm: 80% (4 out of 5)
```

### Cluster 2 (Good Performance)
```
accuracy: mean=97.0%, std=0.4%, min=96.5%, max=97.5%
val_loss: mean=0.11, std=0.03, min=0.08, max=0.15
learning_rate: mean=0.005, std=0.004
lr_scheduler: 10% (mostly static LR)
dropout: 30% (some use it)
```

### Cluster 3 (Suboptimal)
```
accuracy: mean=92.0%, std=4.0%, min=88%, max=96%
val_loss: mean=0.28, std=0.15, min=0.15, max=0.50
learning_rate: mean=0.034, std=0.05 (high variance!)
final_epoch_loss: still_decreasing for low LR experiments
```

### Cluster 4 (Overfitting)
```
train_accuracy: mean=98.5%
val_accuracy: mean=95.8%
train_val_gap: mean=2.7%
hidden_layers: mean_total_neurons=1408
dropout: 0.0
weight_decay: 0.0
```

---

## 🎯 Validation Criteria

Query.ai successfully clusters if:

1. ✅ Separates high-performers (97.5%+) from poor performers (<95%)
2. ✅ Identifies LR as most discriminative feature
3. ✅ Detects overfitting in Cluster 4
4. ✅ Recognizes LR scheduling pattern in top cluster
5. ✅ Provides actionable insights for each cluster
6. ✅ Explains *why* certain configs work better (causation, not just correlation)

---

## 💡 Advanced Analysis Query.ai Could Provide

### Experiment Trajectory Analysis

"Experiments 00 → 17 show progressive optimization:
- 00_baseline (97.0%): Starting point
- 04_arch_batchnorm (97.5%): +0.5% from adding batch norm
- 13_scheduler_step (97.8%): +0.3% from LR scheduling
- 17_best_combined (98.3%): +0.5% from combining all techniques
**Total improvement: 1.3% through systematic optimization**"

### What-If Recommendations

"Based on clustering analysis:
- If you're at baseline (97%), adding LR scheduling gives highest ROI (+0.8%)
- If you have overfitting, add dropout 0.2 (expected +2% val accuracy)
- If training is unstable, reduce LR from 0.1 to 0.01 (expected +8% accuracy)"

### Next Experiment Suggestions

"To push beyond 98.5%:
1. Try learning_rate=0.003 with cosine annealing (interpolate between best)
2. Test dropout=0.3 (current best is 0.25)
3. Experiment with mixed precision training for faster epochs
4. Consider ensemble of experiments 17 and 19"

---

This clustering structure provides clear, actionable insights that help researchers understand what works and why!
