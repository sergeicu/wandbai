"""WandB integration module with proper error handling, logging, and retry logic."""

import wandb
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from logger_config import get_logger
from exceptions import (
    WandBConnectionError,
    WandBAuthenticationError,
    WandBProjectNotFoundError,
    WandBRateLimitError,
    ValidationError
)

logger = get_logger(__name__)


class WandBIntegration:
    """Integration module for fetching and processing WandB experiment data."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WandB API connection.

        Args:
            api_key: WandB API key (optional)

        Raises:
            WandBAuthenticationError: If authentication fails
        """
        logger.info("Initializing WandB integration")
        try:
            if api_key:
                logger.debug("Logging in with provided API key")
                wandb.login(key=api_key)
            self.api = wandb.Api()
            logger.info("WandB API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WandB API: {e}")
            raise WandBAuthenticationError(f"Authentication failed: {e}") from e

    def _validate_entity(self, entity: str) -> None:
        """Validate entity name."""
        if not entity or not entity.strip():
            raise ValidationError("Entity name cannot be empty")
        if len(entity) > 100:
            raise ValidationError("Entity name too long (max 100 characters)")

    def _validate_project(self, project: str) -> None:
        """Validate project name."""
        if not project or not project.strip():
            raise ValidationError("Project name cannot be empty")
        if len(project) > 100:
            raise ValidationError("Project name too long (max 100 characters)")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def get_projects(self, entity: str) -> List[str]:
        """
        Get all projects for an entity.

        Args:
            entity: WandB entity name

        Returns:
            List of project names

        Raises:
            ValidationError: If entity name is invalid
            WandBAuthenticationError: If authentication fails
            WandBConnectionError: If connection fails
        """
        self._validate_entity(entity)
        logger.info(f"Fetching projects for entity: {entity}")

        try:
            projects = self.api.projects(entity=entity)
            project_names = [p.name for p in projects]
            logger.info(f"Found {len(project_names)} projects for {entity}")
            return project_names

        except (ConnectionError, TimeoutError) as e:
            # Re-raise connection/timeout errors directly for retry logic
            logger.warning(f"Transient error fetching projects (will retry): {e}")
            raise

        except Exception as e:
            error_msg = str(e).lower()

            if "authentication" in error_msg or "unauthorized" in error_msg:
                logger.error(f"Authentication error: {e}")
                raise WandBAuthenticationError(f"Authentication failed: {e}") from e
            elif "rate limit" in error_msg:
                logger.error(f"Rate limit exceeded: {e}")
                raise WandBRateLimitError(f"Rate limit exceeded: {e}") from e
            else:
                logger.error(f"Unexpected error fetching projects: {e}")
                raise WandBConnectionError(f"Error fetching projects: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def get_runs(
        self,
        entity: str,
        project: str,
        limit: int = 100
    ) -> List[wandb.apis.public.Run]:
        """
        Fetch runs from a WandB project.

        Args:
            entity: WandB entity name
            project: Project name
            limit: Maximum number of runs to fetch

        Returns:
            List of WandB run objects

        Raises:
            ValidationError: If inputs are invalid
            WandBProjectNotFoundError: If project doesn't exist
            WandBRateLimitError: If rate limit is exceeded
            WandBConnectionError: If connection fails
        """
        self._validate_entity(entity)
        self._validate_project(project)

        logger.info(f"Fetching runs from {entity}/{project} (limit={limit})")

        try:
            runs = self.api.runs(f"{entity}/{project}", per_page=limit)
            run_list = list(runs)
            logger.info(f"Fetched {len(run_list)} runs from {entity}/{project}")
            return run_list

        except (ConnectionError, TimeoutError) as e:
            # Re-raise connection/timeout errors directly for retry logic
            logger.warning(f"Transient error fetching runs (will retry): {e}")
            raise

        except Exception as e:
            error_msg = str(e).lower()

            if "not found" in error_msg or "does not exist" in error_msg:
                logger.error(f"Project not found: {entity}/{project}")
                raise WandBProjectNotFoundError(
                    f"Project {entity}/{project} not found"
                ) from e
            elif "rate limit" in error_msg:
                logger.error(f"Rate limit exceeded: {e}")
                raise WandBRateLimitError(f"Rate limit exceeded: {e}") from e
            else:
                logger.error(f"Unexpected error fetching runs: {e}")
                raise WandBConnectionError(f"Error fetching runs: {e}") from e

    def extract_run_data(self, run: wandb.apis.public.Run) -> Dict[str, Any]:
        """
        Extract relevant data from a WandB run.

        Args:
            run: WandB run object

        Returns:
            Dictionary with metadata, summary, and config

        Raises:
            ValidationError: If run data is invalid
        """
        logger.debug(f"Extracting data from run: {run.id}")

        try:
            # Get summary metrics
            summary = dict(run.summary)

            # Get config
            config = dict(run.config)

            # Get metadata
            metadata = {
                'id': run.id,
                'name': run.name,
                'state': run.state,
                'created_at': run.created_at,
                'updated_at': run.updated_at,
                'runtime': run.summary.get('_runtime', 0),
                'user': run.user.username if run.user else 'unknown',
                'commit': run.commit if hasattr(run, 'commit') else None,
                'tags': run.tags,
                'notes': run.notes,
                'url': run.url
            }

            logger.debug(f"Successfully extracted data from run {run.id}")

            return {
                'metadata': metadata,
                'summary': summary,
                'config': config,
                'run_object': run
            }

        except Exception as e:
            logger.error(f"Error extracting run data: {e}")
            raise ValidationError(f"Failed to extract run data: {e}") from e

    def get_run_history(
        self,
        run: wandb.apis.public.Run,
        keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get historical metrics for a run.

        Args:
            run: WandB run object
            keys: Specific metric keys to fetch (optional)

        Returns:
            DataFrame with historical metrics

        Raises:
            WandBConnectionError: If fetching fails
        """
        logger.debug(f"Fetching history for run: {run.id}")

        try:
            if keys:
                history = run.history(keys=keys)
            else:
                history = run.history()

            logger.debug(f"Fetched {len(history)} history records for run {run.id}")
            return history

        except Exception as e:
            logger.error(f"Error fetching run history: {e}")
            raise WandBConnectionError(f"Failed to fetch run history: {e}") from e

    def get_runs_dataframe(
        self,
        entity: str,
        project: str,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get runs as a pandas DataFrame with key metrics.

        Args:
            entity: WandB entity name
            project: Project name
            limit: Maximum number of runs

        Returns:
            DataFrame with run data

        Raises:
            Same as get_runs()
        """
        logger.info(f"Building DataFrame for {entity}/{project}")

        runs = self.get_runs(entity, project, limit)

        data = []
        for run in runs:
            try:
                run_data = self.extract_run_data(run)

                row = {
                    'id': run_data['metadata']['id'],
                    'name': run_data['metadata']['name'],
                    'state': run_data['metadata']['state'],
                    'created_at': run_data['metadata']['created_at'],
                    'runtime': run_data['metadata']['runtime'],
                    'commit': run_data['metadata']['commit'],
                    'tags': ','.join(run_data['metadata']['tags'])
                    if run_data['metadata']['tags'] else '',
                }

                # Add summary metrics
                for key, value in run_data['summary'].items():
                    if not key.startswith('_') and isinstance(value, (int, float)):
                        row[key] = value

                # Add config values
                for key, value in run_data['config'].items():
                    if isinstance(value, (int, float, str, bool)):
                        row[f'config_{key}'] = value

                data.append(row)

            except Exception as e:
                logger.warning(f"Failed to process run {run.id}: {e}")
                continue

        df = pd.DataFrame(data)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df

    def compare_runs(
        self,
        run_ids: List[str],
        entity: str,
        project: str
    ) -> Dict[str, Any]:
        """
        Compare multiple runs and return differences.

        Args:
            run_ids: List of run IDs to compare
            entity: WandB entity name
            project: Project name

        Returns:
            Dictionary with comparison results

        Raises:
            ValidationError: If inputs are invalid
            WandBConnectionError: If fetching fails
        """
        if not run_ids:
            raise ValidationError("No run IDs provided for comparison")

        logger.info(f"Comparing {len(run_ids)} runs")

        comparison = {
            'metrics': {},
            'configs': {},
            'metadata': []
        }

        for run_id in run_ids:
            try:
                run = self.api.run(f"{entity}/{project}/{run_id}")
                run_data = self.extract_run_data(run)

                comparison['metadata'].append(run_data['metadata'])

                # Collect metrics
                for key, value in run_data['summary'].items():
                    if key not in comparison['metrics']:
                        comparison['metrics'][key] = {}
                    comparison['metrics'][key][run_id] = value

                # Collect configs
                for key, value in run_data['config'].items():
                    if key not in comparison['configs']:
                        comparison['configs'][key] = {}
                    comparison['configs'][key][run_id] = value

            except Exception as e:
                logger.error(f"Error comparing run {run_id}: {e}")
                continue

        logger.info(f"Comparison complete for {len(comparison['metadata'])} runs")
        return comparison

    def get_run_artifacts(self, run: wandb.apis.public.Run) -> List[Dict[str, Any]]:
        """
        Get artifacts logged with a run.

        Args:
            run: WandB run object

        Returns:
            List of artifact metadata

        Raises:
            WandBConnectionError: If fetching fails
        """
        logger.debug(f"Fetching artifacts for run: {run.id}")

        try:
            artifacts = []
            for artifact in run.logged_artifacts():
                artifacts.append({
                    'name': artifact.name,
                    'type': artifact.type,
                    'size': artifact.size,
                    'created_at': artifact.created_at
                })

            logger.debug(f"Found {len(artifacts)} artifacts for run {run.id}")
            return artifacts

        except Exception as e:
            logger.error(f"Error fetching artifacts: {e}")
            raise WandBConnectionError(f"Failed to fetch artifacts: {e}") from e
