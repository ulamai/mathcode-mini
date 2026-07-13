"""Public MathCode Mini research environment."""

from .env import MathCodeMiniEnv
from .grader import grade

__all__ = ["MathCodeMiniEnv", "grade"]
__version__ = "0.1.0"
