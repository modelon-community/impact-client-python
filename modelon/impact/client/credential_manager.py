import logging
import os
import stat
from getpass import getpass
from typing import List, Optional

logger = logging.getLogger(__name__)

_OWNER_ONLY_FILE_MODE = stat.S_IRUSR | stat.S_IWUSR
_OWNER_ONLY_DIR_MODE = stat.S_IRWXU
_GROUP_AND_OTHER_BITS = stat.S_IRWXG | stat.S_IRWXO


class CredentialManager:
    def __init__(
        self,
        file_id: str = "api.key",
        env_names: List[str] = ["MODELON_IMPACT_CLIENT_API_KEY"],
        interactive_help_text: str = "Enter Modelon Impact API key:",
    ):
        self._file_id = file_id
        self._env_names = env_names
        self._interactive_help_text = interactive_help_text

    def get_key_from_env(self) -> Optional[str]:
        for env_name in self._env_names:
            env_value = os.environ.get(env_name)
            if env_value:
                return env_value
        return None

    def _cred_file(self) -> str:
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".impact", self._file_id)

    def get_key_from_file(self) -> Optional[str]:
        credentials_file = self._cred_file()
        if not os.path.isfile(credentials_file):
            return None

        # Earlier versions saved the key file readable by every local user.
        self._restrict_to_owner(credentials_file)
        with open(credentials_file, "r") as credentials:
            return credentials.read().strip()

    def get_key_from_prompt(self) -> str:
        key = getpass(self._interactive_help_text)
        if key == "\x16":
            # This is a getpass Windows bug...
            logger.error("Does not support Ctrl+V on Windows")
            return self.get_key_from_prompt()

        return key

    def write_key_to_file(self, api_key: str) -> None:
        credentials_file = self._cred_file()
        os.makedirs(
            os.path.dirname(credentials_file), mode=_OWNER_ONLY_DIR_MODE, exist_ok=True
        )
        fd = os.open(
            credentials_file,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            _OWNER_ONLY_FILE_MODE,
        )
        with os.fdopen(fd, "w") as credentials:
            # The mode given to `os.open` only applies when it creates the file.
            os.chmod(credentials_file, _OWNER_ONLY_FILE_MODE)
            credentials.write(str(api_key))

        print(
            f"Saved the Modelon Impact API key in plain text to {credentials_file}. "
            f"To keep the key off disk, {self._env_alternative()}"
        )

    def _env_alternative(self) -> str:
        if not self._env_names:
            return "delete the file."
        return (
            f"delete the file and set the environment variable "
            f"{self._env_names[0]} instead."
        )

    @staticmethod
    def _restrict_to_owner(credentials_file: str) -> None:
        # Windows controls file access with ACLs; `chmod` there only toggles
        # the read-only flag.
        if os.name != "posix":
            return
        if not os.stat(credentials_file).st_mode & _GROUP_AND_OTHER_BITS:
            return
        try:
            os.chmod(credentials_file, _OWNER_ONLY_FILE_MODE)
        except OSError:
            logger.warning(
                "Other users may be able to read the Modelon Impact API key in %s. "
                "Make the file readable only by its owner.",
                credentials_file,
            )

    def get_key(self, interactive: bool = False) -> Optional[str]:
        api_key = self.get_key_from_env() or self.get_key_from_file()
        if api_key or not interactive:
            return api_key

        return self.get_key_from_prompt()
