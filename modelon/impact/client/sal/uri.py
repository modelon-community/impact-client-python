"""URI class"""
import sys
import urllib.parse


class URI:
    def __init__(self, content: str):
        # If running on Windows you can get a lot of overhead using 'localhost'
        if sys.platform.startswith("win32") and content.startswith("http://localhost:"):
            content = content.replace("http://localhost:", "http://127.0.0.1:")

        self.content = content

    def resolve(self, **kwargs):
        return self.content.format(**kwargs)

    def _with_path(self, path):
        return URI(urllib.parse.urljoin(self.content + "/", path))

    def __floordiv__(self, other):
        return self._with_path(other)

    def __truediv__(self, other):
        return self._with_path(other)

    def __repr__(self):
        return self.content
