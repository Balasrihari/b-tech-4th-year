"""Enhanced Logging Configuration"""
import sys
from loguru import logger
from pathlib import Path
import os


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    rotation: str = "500 MB",
    retention: str = "30 days"
) -> None:
    """
    Configure enhanced logging with Loguru
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        rotation: Log rotation size
        retention: Log retention period
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # File handler for all logs
    logger.add(
        log_path / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip"
    )
    
    # Error log file
    logger.add(
        log_path / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression="zip"
    )
    
    # API request log file
    logger.add(
        log_path / "api.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {extra[request_id]} | {extra[method]} {extra[path} | {extra[user_id]} - {message}",
        level="INFO",
        rotation=rotation,
        retention=retention,
        filter=lambda record: "request_id" in record["extra"]
    )
    
    # Database query log file
    logger.add(
        log_path / "database.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {extra[query_time]}s | {message}",
        level="DEBUG",
        rotation=rotation,
        retention=retention,
        filter=lambda record: "query_time" in record["extra"]
    )
    
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}")


class APILogger:
    """Context manager for API request logging"""
    
    def __init__(self, request_id: str, method: str, path: str, user_id: str = None):
        self.request_id = request_id
        self.method = method
        self.path = path
        self.user_id = user_id or "anonymous"
    
    def __enter__(self):
        logger.bind(
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            user_id=self.user_id
        ).info(f"API request started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.bind(
                request_id=self.request_id,
                method=self.method,
                path=self.path,
                user_id=self.user_id
            ).error(f"API request failed: {exc_val}")
        else:
            logger.bind(
                request_id=self.request_id,
                method=self.method,
                path=self.path,
                user_id=self.user_id
            ).info(f"API request completed")
        return False


class DBLogger:
    """Context manager for database query logging"""
    
    def __init__(self, query: str):
        self.query = query
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        query_time = time.time() - self.start_time
        
        logger.bind(query_time=f"{query_time:.4f}").debug(
            f"Query executed: {self.query[:100]}..."
        )
        return False


def get_logger(name: str):
    """
    Get a logger with a specific name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Initialize logging on import
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_dir=os.getenv("LOG_DIR", "logs")
)
