import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

from wandb_integration import WandBIntegration
from clustering import ExperimentCluster
from ai_analysis import AIAnalyzer
from code_diff import CodeDiffAnalyzer

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Query - AI-Powered Experiment Management",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .cluster-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .ai-analysis-box {
        background-color: #e8f4ff;
        border-left: 4px solid #0066cc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .code-diff {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
    }
    .diff-add {
        background-color: #1a4d1a;
        color: #90ee90;
    }
    .diff-remove {
        background-color: #4d1a1a;
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_services(wandb_key: str, anthropic_key: str):
    """Initialize all services with caching."""
    wb = WandBIntegration(wandb_key) if wandb_key else None
    ai = AIAnalyzer(anthropic_key) if anthropic_key else None
    diff_analyzer = CodeDiffAnalyzer()
    return wb, ai, diff_analyzer


def format_metric_change(current, previous=None):
    """Format metric change with arrow and percentage."""
    if previous is None or previous == 0:
        return f"{current:.4f}"

    change = current - previous
    pct_change = (change / abs(previous)) * 100

    arrow = "↑" if change > 0 else "↓"
    color = "green" if change > 0 else "red"

    return f"{current:.4f} <span style='color: {color}'>{arrow} {abs(pct_change):.1f}%</span>"


def render_metric_card(title, value, change=None, unit="", color="blue"):
    """Render a metric card."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### {title}")
        if change:
            st.markdown(f"<h2>{value}{unit}</h2>", unsafe_allow_html=True)
            st.markdown(change, unsafe_allow_html=True)
        else:
            st.markdown(f"<h2>{value}{unit}</h2>", unsafe_allow_html=True)


def render_code_diff(diff_text):
    """Render code diff with syntax highlighting."""
    if not diff_text:
        st.info("No code changes available for this run")
        return

    st.markdown("### 💻 Key Code Changes")

    lines = diff_text.split('\n')[:50]  # Show first 50 lines

    formatted_lines = []
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            formatted_lines.append(f'<div class="diff-add">{line}</div>')
        elif line.startswith('-') and not line.startswith('---'):
            formatted_lines.append(f'<div class="diff-remove">{line}</div>')
        else:
            formatted_lines.append(f'<div>{line}</div>')

    diff_html = f'<div class="code-diff">{"".join(formatted_lines)}</div>'
    st.markdown(diff_html, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">Query.ai</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Experiment Management Platform</div>',
                unsafe_allow_html=True)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("Configuration")

        # API Keys
        with st.expander("🔑 API Keys", expanded=True):
            wandb_key = st.text_input(
                "WandB API Key",
                type="password",
                value=os.getenv("WANDB_API_KEY", ""),
                help="Enter your Weights & Biases API key"
            )

            anthropic_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=os.getenv("ANTHROPIC_API_KEY", ""),
                help="Enter your Anthropic API key for AI analysis"
            )

        # Initialize services
        wb_integration, ai_analyzer, diff_analyzer = initialize_services(wandb_key, anthropic_key)

        if not wandb_key:
            st.warning("⚠️ Please enter your WandB API key to continue")
            return

        # Project selection
        st.header("📁 Project")

        entity = st.text_input("WandB Entity (username)", value="", help="Your WandB username or team name")
        project = st.text_input("Project Name", value="", help="WandB project name")

        if not entity or not project:
            st.info("Enter your WandB entity and project name to get started")
            return

        # Load runs
        if st.button("🔄 Load Experiments", type="primary"):
            with st.spinner("Loading experiments from WandB..."):
                st.session_state.runs_df = wb_integration.get_runs_dataframe(entity, project, limit=100)
                st.session_state.entity = entity
                st.session_state.project = project

        if 'runs_df' not in st.session_state or st.session_state.runs_df.empty:
            st.info("Click 'Load Experiments' to fetch your runs")
            return

        # Clustering options
        st.header("🎯 Clustering")
        n_clusters = st.slider("Number of Clusters", 2, 10, 3)

        if st.button("🔬 Analyze & Cluster"):
            with st.spinner("Clustering experiments..."):
                clusterer = ExperimentCluster(method='kmeans', n_clusters=n_clusters)
                st.session_state.clustered_df = clusterer.cluster_runs(st.session_state.runs_df)
                st.session_state.cluster_summary = clusterer.get_cluster_summary(st.session_state.clustered_df)
                st.session_state.cluster_chars = clusterer.get_cluster_characteristics(
                    st.session_state.clustered_df)
                st.success("Clustering complete!")

    # Main content
    if 'runs_df' not in st.session_state:
        st.info("Configure your WandB project in the sidebar to get started")
        return

    df = st.session_state.runs_df

    st.markdown("---")

    # Show summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Experiments", len(df))

    with col2:
        completed = len(df[df['state'] == 'finished']) if 'state' in df.columns else 0
        st.metric("Completed", completed)

    with col3:
        running = len(df[df['state'] == 'running']) if 'state' in df.columns else 0
        st.metric("Running", running)

    with col4:
        if 'cluster' in df.columns:
            st.metric("Clusters", df['cluster'].nunique())
        else:
            st.metric("Clusters", "Not analyzed")

    st.markdown("---")

    # Layout: Sidebar with experiments list + main content
    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.header("Experiments")

        # Show clusters if available
        if 'clustered_df' in st.session_state and 'cluster_chars' in st.session_state:
            st.subheader("Clusters")

            for cluster_id, char in st.session_state.cluster_chars.items():
                cluster_df = st.session_state.clustered_df[
                    st.session_state.clustered_df['cluster'] == cluster_id]
                with st.expander(f"📊 {char} ({len(cluster_df)} runs)"):
                    for idx, row in cluster_df.iterrows():
                        if st.button(row['name'], key=f"cluster_{cluster_id}_{idx}"):
                            st.session_state.selected_run = row
        else:
            # Show all runs
            for idx, row in df.iterrows():
                status_icon = "✅" if row.get('state') == 'finished' else "🔄"
                if st.button(f"{status_icon} {row['name']}", key=f"run_{idx}"):
                    st.session_state.selected_run = row

    with right_col:
        if 'selected_run' not in st.session_state:
            st.info("👈 Select an experiment from the list to view details")
            return

        run = st.session_state.selected_run

        # Run header
        st.header(f"📊 {run['name']}")

        if 'cluster' in run:
            cluster_char = st.session_state.cluster_chars.get(run['cluster'], f"Cluster {run['cluster']}")
            st.markdown(
                f'<span class="cluster-badge" style="background-color: #e0e0e0;">{cluster_char}</span>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Metrics
        st.subheader("Training Metrics")

        metrics_cols = st.columns(4)

        # Extract key metrics
        metric_names = ['accuracy', 'loss', 'epoch', 'learning_rate', 'val_accuracy', 'val_loss']
        available_metrics = [m for m in metric_names if m in run.index and pd.notna(run[m])]

        for idx, metric_name in enumerate(available_metrics[:4]):
            with metrics_cols[idx % 4]:
                value = run[metric_name]
                if isinstance(value, (int, float)):
                    st.metric(metric_name.replace('_', ' ').title(), f"{value:.4f}")

        # Additional metrics in expander
        with st.expander("📈 All Metrics"):
            metric_df = pd.DataFrame([
                {"Metric": k, "Value": v}
                for k, v in run.items()
                if isinstance(v, (int, float)) and not k.startswith('_')
            ])
            st.dataframe(metric_df, use_container_width=True)

        st.markdown("---")

        # Code changes
        if pd.notna(run.get('commit')):
            commit_hash = run['commit']
            st.subheader(f"💻 Code Changes (commit: {commit_hash[:7]})")

            diff = diff_analyzer.get_commit_diff(commit_hash)

            if diff:
                stats = diff_analyzer.get_summary_stats(diff)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Changed", stats['files_changed'])
                with col2:
                    st.metric("Additions", stats['additions'], delta=None)
                with col3:
                    st.metric("Deletions", stats['deletions'], delta=None)

                render_code_diff(diff)
            else:
                st.info("Code diff not available (repository not found or commit not accessible)")

        st.markdown("---")

        # AI Analysis
        if anthropic_key and ai_analyzer:
            st.subheader("🤖 AI Analysis")

            if st.button("Generate AI Insights", type="primary"):
                with st.spinner("Analyzing experiment with AI..."):
                    # Prepare data for analysis
                    run_data = run.to_dict()

                    cluster_data = None
                    all_clusters = None

                    if 'cluster_summary' in st.session_state:
                        cluster_id = run.get('cluster', 0)
                        cluster_data = st.session_state.cluster_summary.get(cluster_id, {})
                        all_clusters = st.session_state.cluster_summary

                    analysis = ai_analyzer.analyze_experiment_cluster(
                        cluster_data or {'run': run_data},
                        all_clusters or {},
                        run_data
                    )

                    st.session_state.ai_analysis = analysis

            if 'ai_analysis' in st.session_state:
                analysis = st.session_state.ai_analysis

                st.markdown('<div class="ai-analysis-box">', unsafe_allow_html=True)

                st.markdown("#### 💡 Summary")
                st.write(analysis.get('summary', 'No summary available'))

                if analysis.get('insights'):
                    st.markdown("#### 🔍 Key Insights")
                    for insight in analysis['insights']:
                        st.markdown(f"- {insight}")

                if analysis.get('recommendations'):
                    st.markdown("#### ✨ Recommended Next Steps")
                    for rec in analysis['recommendations']:
                        st.markdown(f"→ {rec}")

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 Add your Anthropic API key in the sidebar to enable AI-powered insights")

        st.markdown("---")

        # Run configuration
        with st.expander("⚙️ Run Configuration"):
            config_items = {k: v for k, v in run.items() if k.startswith('config_')}
            if config_items:
                config_df = pd.DataFrame([
                    {"Parameter": k.replace('config_', ''), "Value": v}
                    for k, v in config_items.items()
                ])
                st.dataframe(config_df, use_container_width=True)
            else:
                st.info("No configuration parameters logged")


if __name__ == "__main__":
    main()
