import logging
import sys
from inspect import iscoroutinefunction
from logging.handlers import RotatingFileHandler

from src.utils.camel_to_snake import camel_to_snake


# === === === === === === ===
def init_logger(
    max_bytes: int = 5000000,
    backup_count: int = 5,
):
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    file_error_handler = RotatingFileHandler(
        "./logs/errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_error_handler.setLevel(logging.ERROR)

    file_warning_handler = RotatingFileHandler(
        "./logs/warnings.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_warning_handler.setLevel(logging.WARNING)

    file_info_handler = RotatingFileHandler(
        "./logs/info.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_info_handler.setLevel(logging.INFO)

    # file_debug_handler = RotatingFileHandler(
    #     "./logs/debug.log",
    #     maxBytes=max_bytes,
    #     backupCount=backup_count,
    # )
    # file_debug_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            stdout_handler,
            file_error_handler,
            file_warning_handler,
            file_info_handler,
        ],
    )


# === === === === === === ===
def create_custom_logger(
    name: str,
    max_bytes: int = 5000000,
    backup_count: int = 5,
) -> logging.Logger:

    logger = logging.getLogger(name)
    handler = RotatingFileHandler(
        f"./logs/{camel_to_snake(name)}.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


# === === === Log Error decorator === === ===
def log_error(logger: logging.Logger):
    def decorator(func):
        def write_logs(e: Exception, *args, **kwargs):
            logger.error(f"Exception: {e}\n Args: {args}\n Kwargs: {kwargs}", exc_info=True)

        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                write_logs(e, *args, **kwargs)

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                write_logs(e, *args, **kwargs)

        return async_wrapper if iscoroutinefunction(func) else wrapper

    return decorator
