# Quick Start Guide - Query.ai

Welcome to Query.ai! This guide will help you get started with the AI-powered experiment management platform.

## Prerequisites

- Python 3.8 or higher
- WandB account with experiments
- Anthropic API key (for AI analysis)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API keys:**

   Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your keys:
   ```
   WANDB_API_KEY=your_wandb_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

   **How to get API keys:**

   - **WandB API Key**:
     1. Go to https://wandb.ai/settings
     2. Scroll to "API keys" section
     3. Copy your API key

   - **Anthropic API Key**:
     1. Go to https://console.anthropic.com/
     2. Navigate to API Keys
     3. Create a new API key

## Running the Application

### Option 1: Run the Full Application

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Option 2: Test with Demo Data (No WandB account needed)

```bash
python demo.py
```

This will test the clustering and AI analysis with synthetic data.

## Using the Application

### Step 1: Configure Your Project

In the sidebar:
1. Enter your WandB API key
2. Enter your Anthropic API key (optional, for AI analysis)
3. Enter your WandB entity (username or team name)
4. Enter your project name

### Step 2: Load Your Experiments

Click the **"Load Experiments"** button to fetch your runs from WandB.

### Step 3: Cluster Your Experiments

Adjust the number of clusters using the slider, then click **"Analyze & Cluster"**.

The app will group similar experiments based on their metrics and configurations.

### Step 4: Explore Your Results

1. **Browse experiments**: Select an experiment from the sidebar to view details
2. **View metrics**: See training metrics, configurations, and performance
3. **Review code changes**: View git diffs for experiments with commits
4. **Get AI insights**: Click "Generate AI Insights" for recommendations

## Features Overview

### Experiment Management
- Load and browse hundreds of WandB experiments
- Filter by status (completed, running, failed)
- View comprehensive metrics and configurations

### Smart Clustering
- Automatically group similar experiments
- Identify high-performance clusters
- Spot convergence issues and outliers

### AI-Powered Analysis
- Get intelligent insights about your experiments
- Understand why certain configurations work better
- Receive actionable recommendations for next steps

### Code Integration
- View code changes associated with each experiment
- Understand the relationship between code and performance
- Track evolution of your codebase

## Example Workflow

1. **Initial Exploration**: Load your experiments and see the overview
2. **Find Patterns**: Run clustering to identify groups of similar experiments
3. **Deep Dive**: Select the best-performing cluster
4. **Understand**: Use AI analysis to understand what makes these experiments successful
5. **Iterate**: Follow the recommendations to design your next experiments

## Tips for Best Results

### For Clustering
- Use at least 10-15 experiments for meaningful clusters
- Include key metrics like accuracy, loss, learning_rate in your WandB logs
- Tag experiments to make them easier to organize

### For AI Analysis
- Log comprehensive metrics and hyperparameters
- Include git commit information in your runs
- Add notes about experiment goals and hypotheses

### For Code Diffs
- Ensure your code is in a git repository
- Commit before starting experiments
- Use descriptive commit messages

## Troubleshooting

### "Cannot load experiments"
- Verify your WandB API key is correct
- Check that the entity and project names are accurate
- Ensure you have access to the project

### "Clustering failed"
- Make sure you have at least 3 experiments
- Verify your experiments have numeric metrics logged
- Try reducing the number of clusters

### "AI analysis not available"
- Ensure your Anthropic API key is set correctly
- Check your API key has sufficient credits
- Verify internet connectivity

## Architecture

The application consists of several modules:

- **app.py**: Main Streamlit application
- **wandb_integration.py**: WandB API integration
- **clustering.py**: Experiment clustering algorithms
- **ai_analysis.py**: AI-powered insights using Claude
- **code_diff.py**: Git diff extraction and visualization

## Next Steps

1. Explore your existing experiments
2. Try different clustering configurations
3. Use AI insights to guide your research
4. Integrate the tool into your ML workflow

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the README.md for additional documentation
- Review the code documentation in each module

Happy experimenting! 🔬
