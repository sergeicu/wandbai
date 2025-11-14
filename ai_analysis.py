import anthropic
import pandas as pd
from typing import Dict, List, Optional, Any
import json


class AIAnalyzer:
    """AI-powered analysis of experiment runs using Claude."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI analyzer.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze_experiment_cluster(
        self,
        cluster_data: Dict[str, Any],
        all_clusters: Dict[int, Dict[str, Any]],
        selected_run: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a cluster of experiments and generate insights.

        Args:
            cluster_data: Data for the cluster being analyzed
            all_clusters: Data for all clusters (for comparison)
            selected_run: Specific run that's selected (if any)

        Returns:
            Dictionary with analysis results
        """
        prompt = self._build_cluster_analysis_prompt(cluster_data, all_clusters, selected_run)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            analysis = self._parse_analysis_response(response_text)

            return analysis

        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {
                "summary": "Analysis unavailable",
                "insights": [],
                "recommendations": [],
                "key_findings": []
            }

    def _build_cluster_analysis_prompt(
        self,
        cluster_data: Dict[str, Any],
        all_clusters: Dict[int, Dict[str, Any]],
        selected_run: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for cluster analysis."""

        prompt_parts = [
            "You are an AI research assistant analyzing machine learning experiments.",
            "Analyze the following experiment data and provide insights.\n",
            "## Cluster Data:",
            json.dumps(cluster_data, indent=2, default=str),
            "\n## All Clusters (for comparison):",
            json.dumps(all_clusters, indent=2, default=str)
        ]

        if selected_run:
            prompt_parts.extend([
                "\n## Selected Run Details:",
                json.dumps(selected_run, indent=2, default=str)
            ])

        prompt_parts.extend([
            "\nProvide analysis in the following JSON format:",
            "{",
            '  "summary": "Brief 1-2 sentence summary of the key finding",',
            '  "insights": ["insight 1", "insight 2", "insight 3"],',
            '  "recommendations": ["recommendation 1", "recommendation 2"],',
            '  "key_findings": ["finding 1", "finding 2"]',
            "}",
            "\nFocus on:",
            "1. Performance differences between clusters",
            "2. Configuration parameters that impact results",
            "3. Convergence patterns",
            "4. Actionable next steps for improving performance"
        ])

        return "\n".join(prompt_parts)

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured format."""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: structure the plain text response
                return {
                    "summary": response[:200],
                    "insights": [response],
                    "recommendations": [],
                    "key_findings": []
                }

        except json.JSONDecodeError:
            return {
                "summary": response[:200] if response else "Analysis completed",
                "insights": [response] if response else [],
                "recommendations": [],
                "key_findings": []
            }

    def compare_runs(
        self,
        run1: Dict[str, Any],
        run2: Dict[str, Any],
        code_diff: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare two runs and analyze differences.

        Args:
            run1: First run data
            run2: Second run data
            code_diff: Code diff between runs (if available)

        Returns:
            Comparison analysis
        """
        prompt_parts = [
            "Compare these two ML experiment runs and explain the differences:\n",
            "## Run 1:",
            json.dumps(run1, indent=2, default=str),
            "\n## Run 2:",
            json.dumps(run2, indent=2, default=str)
        ]

        if code_diff:
            prompt_parts.extend([
                "\n## Code Changes:",
                code_diff
            ])

        prompt_parts.extend([
            "\nProvide comparison in JSON format:",
            "{",
            '  "performance_difference": "Description of performance changes",',
            '  "config_differences": ["difference 1", "difference 2"],',
            '  "likely_causes": ["cause 1", "cause 2"],',
            '  "recommendation": "What to try next"',
            "}"
        ])

        prompt = "\n".join(prompt_parts)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            return self._parse_analysis_response(response_text)

        except Exception as e:
            print(f"Error in run comparison: {e}")
            return {
                "performance_difference": "Analysis unavailable",
                "config_differences": [],
                "likely_causes": [],
                "recommendation": ""
            }

    def suggest_experiments(
        self,
        current_results: Dict[str, Any],
        goal: str = "improve performance"
    ) -> List[str]:
        """
        Suggest new experiments based on current results.

        Args:
            current_results: Summary of current experiment results
            goal: Research goal

        Returns:
            List of experiment suggestions
        """
        prompt = f"""Based on these experiment results, suggest 3-5 concrete next experiments to try.
Goal: {goal}

Current Results:
{json.dumps(current_results, indent=2, default=str)}

Provide suggestions as a JSON array:
["suggestion 1", "suggestion 2", "suggestion 3"]

Each suggestion should be specific and actionable, including parameter values to try."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return [response_text]

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return ["Unable to generate suggestions at this time."]

    def analyze_code_changes(
        self,
        code_diff: str,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze how code changes affected metrics.

        Args:
            code_diff: Git diff of code changes
            before_metrics: Metrics before change
            after_metrics: Metrics after change

        Returns:
            Analysis of code impact
        """
        prompt = f"""Analyze how these code changes affected the ML model performance:

## Code Changes:
{code_diff}

## Metrics Before:
{json.dumps(before_metrics, indent=2)}

## Metrics After:
{json.dumps(after_metrics, indent=2)}

Provide analysis in JSON format:
{{
  "impact_summary": "Brief summary of impact",
  "metric_changes": ["change 1", "change 2"],
  "code_explanation": "What the code changes do",
  "causation_analysis": "Why these changes affected metrics this way"
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            return self._parse_analysis_response(response_text)

        except Exception as e:
            print(f"Error analyzing code changes: {e}")
            return {
                "impact_summary": "Analysis unavailable",
                "metric_changes": [],
                "code_explanation": "",
                "causation_analysis": ""
            }
