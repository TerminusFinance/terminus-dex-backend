from typing import TypedDict


class DatabaseConfigDict(TypedDict):
    host: str
    port: int
    db_name: str
    user: str
    password: str
