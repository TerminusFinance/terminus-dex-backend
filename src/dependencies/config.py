from typing import Annotated

from fastapi import Depends
from src.config import Config, ConfigManager


# === === === === === === ===
def get_config_manager() -> ConfigManager:

    return ConfigManager()


# === === === === === === ===
def get_config(
    config_manager: Annotated[ConfigManager, Depends(get_config_manager)],
) -> Config:

    return ConfigManager().get_config()
