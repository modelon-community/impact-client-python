"""URI class."""
from __future__ import annotations

import sys
import urllib.parse
from typing import Any


class URI:
    def __init__(self, content: str):
        # If running on Windows you can get a lot of overhead using 'localhost'
        if sys.platform.startswith("win32") and content.startswith("http://localhost:"):
            content = content.replace("http://localhost:", "http://127.0.0.1:")

        self.content = content

    def resolve(self, **kwargs: Any) -> str:
        return self.content.format(**kwargs)

    def _with_path(self, path: str) -> URI:
        return URI(urllib.parse.urljoin(self.content + "/", path.lstrip("/")))

    def __floordiv__(self, other: str) -> URI:
        return self._with_path(other)

    def __truediv__(self, other: str) -> URI:
        return self._with_path(other)

    def __repr__(self) -> str:
        return self.content
