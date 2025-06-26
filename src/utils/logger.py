"""
Logging utilities for Student Insights Pipeline
"""

import logging
import structlog
from typing import Any, Dict
from ..config import get_config

config = get_config()


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Configured structlog logger
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, config.LOG_LEVEL.upper()),
    )
    
    return structlog.get_logger(name)


def log_function_call(func_name: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Create a log context for function calls
    
    Args:
        func_name: Name of the function being called
        **kwargs: Additional context to log
        
    Returns:
        Dictionary with logging context
    """
    return {
        "function": func_name,
        "environment": config.ENVIRONMENT,
        **kwargs
    }


def log_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a log context for errors
    
    Args:
        error: The exception that occurred
        context: Additional context
        
    Returns:
        Dictionary with error logging context
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "environment": config.ENVIRONMENT,
    }
    
    if context:
        error_context.update(context)
        
    return error_context
