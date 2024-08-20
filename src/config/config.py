from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.types import DatabaseConfigDict
from src.types.ton.ton_address_annotated import TonAddressType

# === === === === === === ===


class App(BaseSettings):

    name: str = "Terminus-Dex"
    version: str = "0.0.1"

    referral_code_length: int = 10


# === === === === === === ===


class Account(BaseSettings):

    payload_lifetime_minutes: int = 60
    payload_creating_max_tries: int = 3

    token_ttl_minutes: int = 60 * 48
    token_update_threshold_minutes: int = 60 * 24
    token_cookie_key: str
    token_secret: SecretStr
    token_algorithm: str


# === === === === === === ===


class Database(BaseSettings):

    host: str
    port: int
    database: str
    user: str
    password: SecretStr

    def as_dict(self) -> DatabaseConfigDict:
        return {
            "host": self.host,
            "port": self.port,
            "db_name": self.database,
            "user": self.user,
            "password": self.password.get_secret_value(),
        }


# === === === === === === ===


class TonConsole(BaseSettings):

    api_key: SecretStr
    is_testnet: bool = False
    max_retries: int = 10


# === === === === === === ===


class TonDex(BaseSettings):

    router_address: TonAddressType
    proxy_ton_address: TonAddressType


# === === === === === === ===


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    debug: bool = False

    app: App
    database: Database
    account: Account
    ton_console: TonConsole
    ton_dex: TonDex

    # === === === === === === ===

    def get_workchain_id(self) -> int:
        if self.ton_console.is_testnet:
            return -3
        else:
            return -239


# === === === === === === ===
