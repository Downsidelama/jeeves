from enum import Enum


class PipeLineStatus(Enum):
    """Enum which helps making status human readable in code."""
    IN_PROGRESS = 1
    FAILED = 2
    SUCCESS = 3
    IN_QUEUE = 4
