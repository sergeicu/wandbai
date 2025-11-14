"""Tests for WandB integration module."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from wandb_integration import WandBIntegration
from exceptions import (
    WandBConnectionError,
    WandBAuthenticationError,
    WandBProjectNotFoundError,
    WandBRateLimitError
)


class TestWandBIntegration:
    """Test WandB integration class."""

    @pytest.mark.unit
    def test_init_with_api_key(self, mock_wandb_api):
        """Test initialization with API key."""
        with patch('wandb_integration.wandb') as mock_wandb:
            mock_wandb.Api.return_value = mock_wandb_api
            integration = WandBIntegration(api_key="test_key")
            mock_wandb.login.assert_called_once_with(key="test_key")
            assert integration.api == mock_wandb_api

    @pytest.mark.unit
    def test_init_without_api_key(self, mock_wandb_api):
        """Test initialization without API key."""
        with patch('wandb_integration.wandb') as mock_wandb:
            mock_wandb.Api.return_value = mock_wandb_api
            integration = WandBIntegration()
            mock_wandb.login.assert_not_called()
            assert integration.api == mock_wandb_api

    @pytest.mark.unit
    def test_get_projects_success(self, mock_wandb_api):
        """Test successful project fetching."""
        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            projects = integration.get_projects("test-entity")
            assert projects == ['test-project']

    @pytest.mark.unit
    def test_get_projects_authentication_error(self, mock_wandb_api):
        """Test project fetching with authentication error."""
        mock_wandb_api.projects.side_effect = Exception("Authentication failed")

        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            with pytest.raises(WandBAuthenticationError):
                integration.get_projects("test-entity")

    @pytest.mark.unit
    def test_get_projects_connection_error(self, mock_wandb_api):
        """Test project fetching with connection error."""
        mock_wandb_api.projects.side_effect = ConnectionError("Network error")

        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            # After retries exhausted, ConnectionError is raised
            with pytest.raises(ConnectionError):
                integration.get_projects("test-entity")

    @pytest.mark.unit
    def test_get_runs_success(self, mock_wandb_api, mock_wandb_run):
        """Test successful runs fetching."""
        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            runs = integration.get_runs("test-entity", "test-project")
            assert len(runs) == 1
            assert runs[0] == mock_wandb_run

    @pytest.mark.unit
    def test_get_runs_project_not_found(self, mock_wandb_api):
        """Test runs fetching with non-existent project."""
        mock_wandb_api.runs.side_effect = Exception("Project not found")

        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            with pytest.raises(WandBProjectNotFoundError):
                integration.get_runs("test-entity", "nonexistent-project")

    @pytest.mark.unit
    def test_get_runs_rate_limit(self, mock_wandb_api):
        """Test runs fetching with rate limit error."""
        mock_wandb_api.runs.side_effect = Exception("Rate limit exceeded")

        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            with pytest.raises(WandBRateLimitError):
                integration.get_runs("test-entity", "test-project")

    @pytest.mark.unit
    def test_extract_run_data(self, mock_wandb_run):
        """Test extracting data from a run."""
        with patch('wandb_integration.wandb.Api'):
            integration = WandBIntegration()
            data = integration.extract_run_data(mock_wandb_run)

            assert 'metadata' in data
            assert 'summary' in data
            assert 'config' in data
            assert data['metadata']['id'] == 'run_123'
            assert data['summary']['accuracy'] == 0.95

    @pytest.mark.unit
    def test_get_runs_dataframe(self, mock_wandb_api, mock_wandb_run):
        """Test getting runs as DataFrame."""
        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            df = integration.get_runs_dataframe("test-entity", "test-project")

            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert 'id' in df.columns
            assert 'name' in df.columns
            assert 'accuracy' in df.columns

    @pytest.mark.unit
    def test_retry_on_transient_failure(self, mock_wandb_api):
        """Test retry logic on transient failures."""
        # First call fails, second succeeds
        mock_wandb_api.runs.side_effect = [
            ConnectionError("Temporary network error"),
            [Mock()]
        ]

        with patch('wandb_integration.wandb.Api', return_value=mock_wandb_api):
            integration = WandBIntegration()
            # Should retry and succeed
            runs = integration.get_runs("test-entity", "test-project")
            assert len(runs) > 0
            assert mock_wandb_api.runs.call_count == 2


class TestWandBIntegrationValidation:
    """Test input validation."""

    @pytest.mark.unit
    def test_invalid_entity_name(self):
        """Test validation of entity name."""
        from exceptions import ValidationError

        with patch('wandb_integration.wandb.Api'):
            integration = WandBIntegration()
            with pytest.raises(ValidationError):
                integration.get_projects("")  # Empty entity name

    @pytest.mark.unit
    def test_invalid_project_name(self):
        """Test validation of project name."""
        from exceptions import ValidationError

        with patch('wandb_integration.wandb.Api'):
            integration = WandBIntegration()
            with pytest.raises(ValidationError):
                integration.get_runs("test-entity", "")  # Empty project name
