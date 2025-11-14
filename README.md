# Query.ai - AI-Powered Experiment Management Platform

An AI-powered experiment management platform that helps ML researchers analyze metrics, code diffs, and results to cluster runs, generate insights, and suggest next steps.

## Features

- **WandB Integration**: Connect to your Weights & Biases projects and fetch experiment runs
- **Smart Clustering**: Automatically group similar experiments using ML clustering algorithms
- **AI Analysis**: Get AI-powered insights and recommendations using Claude
- **Code Diff Visualization**: View code changes associated with each experiment
- **Metrics Dashboard**: Beautiful visualization of training metrics and results
- **Multi-user Support**: Designed to handle hundreds of experiments from multiple users

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd wandbai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
WANDB_API_KEY=your_wandb_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Enter your configuration:
   - WandB API Key
   - Anthropic API Key (for AI analysis)
   - WandB Entity (username/team)
   - Project name

4. Click "Load Experiments" to fetch your runs

5. Use "Analyze & Cluster" to group similar experiments

6. Select an experiment to view:
   - Training metrics
   - Code changes
   - AI-powered insights and recommendations

## Architecture

### Modules

- **wandb_integration.py**: Handles all interactions with WandB API
- **clustering.py**: Implements experiment clustering using sklearn
- **ai_analysis.py**: Provides AI-powered analysis using Claude API
- **code_diff.py**: Extracts and formats git diffs
- **app.py**: Main Streamlit application

### Tech Stack

- **Frontend**: Streamlit
- **ML Libraries**: scikit-learn, pandas, numpy
- **APIs**: WandB API, Anthropic Claude API
- **Version Control**: GitPython

## API Keys

### Getting a WandB API Key
1. Go to https://wandb.ai/settings
2. Scroll to "API keys" section
3. Copy your API key

### Getting an Anthropic API Key
1. Go to https://console.anthropic.com/
2. Navigate to API Keys
3. Create a new API key

## Features Roadmap

- [ ] Real-time experiment monitoring
- [ ] Automated hypothesis generation
- [ ] Literature review integration
- [ ] Experiment suggestion engine
- [ ] Team collaboration features
- [ ] Advanced visualizations
- [ ] Export and reporting tools

## Vision

Query is the first step toward building fully autonomous AI agents capable of performing independent research in Machine Learning and Data Science. By helping researchers better understand their experiments today, we're collecting the data and building the tools needed for AI systems that can independently propose hypotheses, design experiments, execute them, analyze results, and iterate—pushing the boundaries of scientific discovery without human intervention.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
