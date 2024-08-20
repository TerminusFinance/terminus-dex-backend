from fastapi import FastAPI
from src.server import create_server


# === === === === === === ===
def init_application() -> FastAPI:
    server = create_server()

    return server


# === === === === === === ===
server = init_application()
