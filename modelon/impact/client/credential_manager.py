import os

from getpass import getpass


class CredentialManager:
    def get_key_from_env(self):
        return os.environ.get("MODELON_IMPACT_CLIENT_API_KEY")

    def _cred_file(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".impact", "api.key")

    def get_key_from_file(self):
        credentials_file = self._cred_file()
        if not os.path.isfile(credentials_file):
            return None

        with open(credentials_file, "r") as credentials:
            return credentials.read().strip()

    def get_key_from_prompt(self):
        return getpass("Enter API key:")

    def write_key_to_file(self, api_key):
        credentials_file = self._cred_file()
        os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
        with open(credentials_file, "w") as credentials:
            credentials.write(str(api_key))

    def get_key(self, interactive=False):
        api_key = self.get_key_from_env() or self.get_key_from_file()
        if api_key or not interactive:
            return api_key

        return self.get_key_from_prompt()
