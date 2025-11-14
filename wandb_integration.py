import wandb
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime
import os


class WandBIntegration:
    """Integration module for fetching and processing WandB experiment data."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize WandB API connection."""
        if api_key:
            wandb.login(key=api_key)
        self.api = wandb.Api()

    def get_projects(self, entity: str) -> List[str]:
        """Get all projects for an entity."""
        try:
            projects = self.api.projects(entity=entity)
            return [p.name for p in projects]
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def get_runs(self, entity: str, project: str, limit: int = 100) -> List[wandb.apis.public.Run]:
        """Fetch runs from a WandB project."""
        try:
            runs = self.api.runs(f"{entity}/{project}", per_page=limit)
            return list(runs)
        except Exception as e:
            print(f"Error fetching runs: {e}")
            return []

    def extract_run_data(self, run: wandb.apis.public.Run) -> Dict[str, Any]:
        """Extract relevant data from a WandB run."""
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

            return {
                'metadata': metadata,
                'summary': summary,
                'config': config,
                'run_object': run
            }
        except Exception as e:
            print(f"Error extracting run data: {e}")
            return {}

    def get_run_history(self, run: wandb.apis.public.Run, keys: Optional[List[str]] = None) -> pd.DataFrame:
        """Get historical metrics for a run."""
        try:
            if keys:
                history = run.history(keys=keys)
            else:
                history = run.history()
            return history
        except Exception as e:
            print(f"Error fetching run history: {e}")
            return pd.DataFrame()

    def get_runs_dataframe(self, entity: str, project: str, limit: int = 100) -> pd.DataFrame:
        """Get runs as a pandas DataFrame with key metrics."""
        runs = self.get_runs(entity, project, limit)

        data = []
        for run in runs:
            run_data = self.extract_run_data(run)
            if run_data:
                row = {
                    'id': run_data['metadata']['id'],
                    'name': run_data['metadata']['name'],
                    'state': run_data['metadata']['state'],
                    'created_at': run_data['metadata']['created_at'],
                    'runtime': run_data['metadata']['runtime'],
                    'commit': run_data['metadata']['commit'],
                    'tags': ','.join(run_data['metadata']['tags']) if run_data['metadata']['tags'] else '',
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

        return pd.DataFrame(data)

    def compare_runs(self, run_ids: List[str], entity: str, project: str) -> Dict[str, Any]:
        """Compare multiple runs and return differences."""
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
                print(f"Error comparing run {run_id}: {e}")

        return comparison

    def get_run_artifacts(self, run: wandb.apis.public.Run) -> List[Dict[str, Any]]:
        """Get artifacts logged with a run."""
        try:
            artifacts = []
            for artifact in run.logged_artifacts():
                artifacts.append({
                    'name': artifact.name,
                    'type': artifact.type,
                    'size': artifact.size,
                    'created_at': artifact.created_at
                })
            return artifacts
        except Exception as e:
            print(f"Error fetching artifacts: {e}")
            return []
