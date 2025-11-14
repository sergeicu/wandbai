"""Custom exceptions for Query.ai application."""


class QueryAIException(Exception):
    """Base exception for Query.ai."""
    pass


class WandBConnectionError(QueryAIException):
    """Raised when WandB API connection fails."""
    pass


class WandBAuthenticationError(QueryAIException):
    """Raised when WandB authentication fails."""
    pass


class WandBProjectNotFoundError(QueryAIException):
    """Raised when WandB project is not found."""
    pass


class WandBRateLimitError(QueryAIException):
    """Raised when WandB API rate limit is exceeded."""
    pass


class AIAnalysisError(QueryAIException):
    """Raised when AI analysis fails."""
    pass


class AnthropicAPIError(QueryAIException):
    """Raised when Anthropic API calls fail."""
    pass


class AnthropicRateLimitError(QueryAIException):
    """Raised when Anthropic API rate limit is exceeded."""
    pass


class ClusteringError(QueryAIException):
    """Raised when clustering operations fail."""
    pass


class InsufficientDataError(QueryAIException):
    """Raised when there's not enough data for an operation."""
    pass


class GitRepositoryError(QueryAIException):
    """Raised when git repository operations fail."""
    pass


class CommitNotFoundError(QueryAIException):
    """Raised when a git commit is not found."""
    pass


class ConfigurationError(QueryAIException):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(QueryAIException):
    """Raised when input validation fails."""
    pass
