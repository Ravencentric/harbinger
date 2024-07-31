from __future__ import annotations


class HarbingerException(Exception):
    """Base Exception"""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class ExecutableNotFoundError(HarbingerException):
    """Raised when an executable is missing"""
    def __init__(self, executable: str) -> None:
        self.executable = executable
        super().__init__(
            f"The executable '{executable}' could not be found. Please ensure it is installed and included in the system's PATH environment variable."
        )