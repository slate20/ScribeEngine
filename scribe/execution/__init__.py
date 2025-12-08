"""
Execution context module for ScribeEngine.

Provides sandboxed Python execution for template code blocks.
"""

from scribe.execution.context import ExecutionContext
from scribe.execution.builtins import get_safe_builtins

__all__ = ["ExecutionContext", "get_safe_builtins"]
