from enum import Enum


class GithubEventStatus(Enum):
    """Makes the GitHub event status more human readable in code."""
    ERROR = "error"
    FAILURE = "failure"
    PENDING = "pending"
    SUCCESS = "success"
