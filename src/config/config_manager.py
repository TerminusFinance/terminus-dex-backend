import logging

from src.utils.singleton import SingletonMeta

from .config import Config

logger = logging.getLogger("ConfigManager")


class ConfigManager(metaclass=SingletonMeta):
    config_instance: Config | None = None

    def get_config(self) -> Config:
        if self.config_instance is None:
            logger.info("Initializing config...")
            self.config_instance = Config()  # type: ignore

        return self.config_instance

    def update_config(self) -> None:
        logger.info("Updating config...")
        self.config_instance = Config()  # type: ignore
