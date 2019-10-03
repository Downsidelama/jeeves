from enum import Enum


class PipeLineStatus(Enum):
    IN_PROGRESS = 1
    FAILED = 2
    SUCCESS = 3
    IN_QUEUE = 4
