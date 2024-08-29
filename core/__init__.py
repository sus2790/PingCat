import gc

import dotenv

dotenv.load_dotenv()
del dotenv
gc.collect()

from core import core
from core.core import (
    arc_client,
    bot,
    handle_ping_command,
    httpx_client,
)

__all__ = ["arc_client", "bot", "core", "handle_ping_command", "httpx_client"]
