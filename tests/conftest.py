"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile
import git


@pytest.fixture
def sample_run_data():
    """Sample run data for testing."""
    return {
        'metadata': {
            'id': 'run_123',
            'name': 'test-experiment',
            'state': 'finished',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T01:00:00',
            'runtime': 3600,
            'user': 'testuser',
            'commit': 'abc123',
            'tags': ['test', 'experiment'],
            'notes': 'Test run',
            'url': 'https://wandb.ai/test/project/runs/run_123'
        },
        'summary': {
            'accuracy': 0.95,
            'loss': 0.05,
            'val_accuracy': 0.93,
            'val_loss': 0.07,
            'epoch': 50
        },
        'config': {
            'learning_rate': 0.001,
            'batch_size': 32,
            'optimizer': 'adam',
            'epochs': 50
        }
    }


@pytest.fixture
def sample_runs_dataframe():
    """Sample runs DataFrame for testing."""
    np.random.seed(42)
    data = []
    for i in range(20):
        data.append({
            'id': f'run_{i}',
            'name': f'experiment-{i:03d}',
            'state': 'finished',
            'created_at': f'2024-01-{i+1:02d}T00:00:00',
            'runtime': np.random.uniform(100, 500),
            'commit': f'abc{i:03d}',
            'tags': 'test',
            'accuracy': np.random.uniform(0.7, 0.95),
            'loss': np.random.uniform(0.05, 0.3),
            'learning_rate': np.random.choice([0.0001, 0.001, 0.01]),
            'batch_size': np.random.choice([16, 32, 64]),
            'config_learning_rate': np.random.choice([0.0001, 0.001, 0.01]),
            'config_batch_size': np.random.choice([16, 32, 64])
        })
    return pd.DataFrame(data)


@pytest.fixture
def mock_wandb_run():
    """Mock WandB run object."""
    run = Mock()
    run.id = 'run_123'
    run.name = 'test-experiment'
    run.state = 'finished'
    run.created_at = '2024-01-01T00:00:00'
    run.updated_at = '2024-01-01T01:00:00'
    run.user = Mock(username='testuser')
    run.commit = 'abc123'
    run.tags = ['test']
    run.notes = 'Test run'
    run.url = 'https://wandb.ai/test/project/runs/run_123'
    run.summary = {
        'accuracy': 0.95,
        'loss': 0.05,
        '_runtime': 3600
    }
    run.config = {
        'learning_rate': 0.001,
        'batch_size': 32
    }
    run.history = Mock(return_value=pd.DataFrame({
        'accuracy': [0.8, 0.85, 0.9, 0.95],
        'loss': [0.2, 0.15, 0.1, 0.05]
    }))
    return run


@pytest.fixture
def mock_wandb_api(mock_wandb_run):
    """Mock WandB API object."""
    api = Mock()
    api.runs = Mock(return_value=[mock_wandb_run])
    api.run = Mock(return_value=mock_wandb_run)

    # Mock projects
    project = Mock()
    project.name = 'test-project'
    api.projects = Mock(return_value=[project])

    return api


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client."""
    client = Mock()

    # Mock message response
    message = Mock()
    content = Mock()
    content.text = '{"summary": "Test summary", "insights": ["Insight 1"], "recommendations": ["Rec 1"], "key_findings": ["Finding 1"]}'
    message.content = [content]

    client.messages.create = Mock(return_value=message)

    return client


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize repo
        repo = git.Repo.init(repo_path)

        # Create a test file
        test_file = repo_path / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n")

        # First commit
        repo.index.add(['test.py'])
        repo.index.commit("Initial commit")

        # Modify file
        test_file.write_text("def hello():\n    print('hello world')\n")

        # Second commit
        repo.index.add(['test.py'])
        repo.index.commit("Update hello function")

        yield repo_path


@pytest.fixture
def sample_cluster_summary():
    """Sample cluster summary for testing."""
    return {
        0: {
            'size': 7,
            'runs': ['exp-001', 'exp-002', 'exp-003'],
            'stats': {
                'accuracy': {'mean': 0.92, 'std': 0.02, 'min': 0.90, 'max': 0.95},
                'loss': {'mean': 0.08, 'std': 0.02, 'min': 0.05, 'max': 0.10}
            }
        },
        1: {
            'size': 5,
            'runs': ['exp-004', 'exp-005'],
            'stats': {
                'accuracy': {'mean': 0.80, 'std': 0.03, 'min': 0.75, 'max': 0.85},
                'loss': {'mean': 0.20, 'std': 0.05, 'min': 0.15, 'max': 0.25}
            }
        }
    }


@pytest.fixture
def sample_code_diff():
    """Sample git diff for testing."""
    return """diff --git a/model.py b/model.py
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
