import gc

import dotenv

dotenv.load_dotenv()
del dotenv
gc.collect()

from core import core

from core.core import (
    ping_command,
    arc_client,
    bot,
    client,
)

__all__ = [
    "arc_client",
    "bot",
    "client",
    "core",
    "ping_command",
]