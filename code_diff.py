import git
from typing import Optional, Dict, List
import os


class CodeDiffAnalyzer:
    """Analyze code differences between experiment runs."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize code diff analyzer.

        Args:
            repo_path: Path to git repository (if None, use current directory)
        """
        self.repo_path = repo_path or os.getcwd()
        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            self.repo = None
            print(f"Warning: {self.repo_path} is not a git repository")

    def get_commit_diff(self, commit_hash: str, parent: str = "HEAD~1") -> Optional[str]:
        """
        Get diff for a specific commit.

        Args:
            commit_hash: Commit hash to analyze
            parent: Parent commit to compare against

        Returns:
            Diff string or None if not available
        """
        if not self.repo:
            return None

        try:
            commit = self.repo.commit(commit_hash)
            if commit.parents:
                parent_commit = commit.parents[0]
                diff = self.repo.git.diff(parent_commit.hexsha, commit.hexsha)
            else:
                # First commit has no parent
                diff = self.repo.git.show(commit.hexsha)

            return diff

        except Exception as e:
            print(f"Error getting commit diff: {e}")
            return None

    def get_diff_between_commits(self, commit1: str, commit2: str) -> Optional[str]:
        """
        Get diff between two commits.

        Args:
            commit1: First commit hash
            commit2: Second commit hash

        Returns:
            Diff string or None if not available
        """
        if not self.repo:
            return None

        try:
            diff = self.repo.git.diff(commit1, commit2)
            return diff
        except Exception as e:
            print(f"Error getting diff between commits: {e}")
            return None

    def parse_diff(self, diff_text: str) -> List[Dict[str, any]]:
        """
        Parse diff text into structured format.

        Args:
            diff_text: Raw diff text

        Returns:
            List of file changes with details
        """
        if not diff_text:
            return []

        changes = []
        current_file = None
        current_hunks = []

        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file
                if current_file:
                    changes.append({
                        'file': current_file,
                        'hunks': current_hunks
                    })

                # Start new file
                parts = line.split(' ')
                if len(parts) >= 3:
                    current_file = parts[2].replace('a/', '')
                current_hunks = []

            elif line.startswith('@@'):
                # New hunk
                current_hunks.append({
                    'header': line,
                    'lines': []
                })

            elif current_hunks and (line.startswith('+') or line.startswith('-') or line.startswith(' ')):
                current_hunks[-1]['lines'].append(line)

        # Save last file
        if current_file:
            changes.append({
                'file': current_file,
                'hunks': current_hunks
            })

        return changes

    def get_changed_files(self, commit_hash: str) -> List[str]:
        """
        Get list of files changed in a commit.

        Args:
            commit_hash: Commit hash

        Returns:
            List of changed file paths
        """
        if not self.repo:
            return []

        try:
            commit = self.repo.commit(commit_hash)
            if commit.parents:
                parent = commit.parents[0]
                diff = parent.diff(commit)
            else:
                diff = commit.diff(git.NULL_TREE)

            return [item.a_path or item.b_path for item in diff]

        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []

    def get_commit_message(self, commit_hash: str) -> Optional[str]:
        """
        Get commit message.

        Args:
            commit_hash: Commit hash

        Returns:
            Commit message or None
        """
        if not self.repo:
            return None

        try:
            commit = self.repo.commit(commit_hash)
            return commit.message
        except Exception as e:
            print(f"Error getting commit message: {e}")
            return None

    def format_diff_for_display(self, diff_text: str, max_lines: int = 100) -> str:
        """
        Format diff for better display in UI.

        Args:
            diff_text: Raw diff text
            max_lines: Maximum number of lines to include

        Returns:
            Formatted diff text
        """
        if not diff_text:
            return "No code changes available"

        lines = diff_text.split('\n')
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append(f"\n... (truncated, {len(diff_text.split(chr(10))) - max_lines} more lines)")

        return '\n'.join(lines)

    def get_summary_stats(self, diff_text: str) -> Dict[str, int]:
        """
        Get summary statistics from diff.

        Args:
            diff_text: Raw diff text

        Returns:
            Dictionary with stats (lines added, removed, files changed)
        """
        if not diff_text:
            return {'additions': 0, 'deletions': 0, 'files_changed': 0}

        lines = diff_text.split('\n')
        additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
        files_changed = sum(1 for line in lines if line.startswith('diff --git'))

        return {
            'additions': additions,
            'deletions': deletions,
            'files_changed': files_changed
        }
