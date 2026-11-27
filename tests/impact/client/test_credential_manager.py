import os
import re
import unittest.mock

import pytest

from modelon.impact.client.credential_manager import CredentialManager
from modelon.impact.client.exceptions import InsecureCredentialsFileError


@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_API_KEY", "api_key_from_env")


@pytest.fixture
def mock_env_missing(monkeypatch):
    monkeypatch.delenv("MODELON_IMPACT_CLIENT_API_KEY", raising=False)


@pytest.fixture
def mock_home_dir_api_key(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    impact = home / ".impact"
    impact.mkdir()
    api_key_file = home / ".impact" / "api.key"
    api_key_file.write_text("api_key_from_file")

    monkeypatch.setattr(os.path, "expanduser", lambda path: str(home))


@pytest.fixture
def mock_home_dir_with_empty_impact_dir(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    impact = home / ".impact"
    impact.mkdir()

    monkeypatch.setattr(os.path, "expanduser", lambda path: str(home))


@pytest.fixture
def mock_home_dir_no_api_key(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setattr(os.path, "expanduser", lambda path: str(home))


def test_credential_manager_from_env_defined(mock_env_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key_from_env()


def test_credential_manager_from_env_not_defined(mock_env_missing):
    cred_manager = CredentialManager()
    assert cred_manager.get_key_from_env() is None


def test_credential_manager_from_file(mock_home_dir_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key_from_file()


def test_credential_manager_from_file_does_not_exist(mock_home_dir_no_api_key):
    cred_manager = CredentialManager()
    assert cred_manager.get_key_from_file() is None


def test_credential_manager_write_to_file(mock_home_dir_no_api_key):
    cred_manager = CredentialManager()
    cred_manager.write_key_to_file("a_new_api_key")
    assert "a_new_api_key" == cred_manager.get_key_from_file()


@unittest.mock.patch("modelon.impact.client.credential_manager.getpass")
def test_credential_manager_from_getpass(getpass):
    getpass.return_value = "api_key_from_getpass"
    cred_manager = CredentialManager()
    assert "api_key_from_getpass" == cred_manager.get_key_from_prompt()


def test_credential_manager_get_key_nothing(mock_home_dir_no_api_key, mock_env_missing):
    cred_manager = CredentialManager()
    assert cred_manager.get_key(interactive=False) is None


@unittest.mock.patch("modelon.impact.client.credential_manager.getpass")
def test_credential_manager_get_key_interactive(
    getpass, mock_home_dir_no_api_key, mock_env_missing
):
    getpass.return_value = "api_key_from_getpass"
    cred_manager = CredentialManager()
    assert "api_key_from_getpass" == cred_manager.get_key(interactive=True)


def test_credential_manager_get_key_only_env(
    mock_home_dir_no_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=False)


def test_credential_manager_get_key_only_file(mock_home_dir_api_key, mock_env_missing):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key(interactive=False)


def test_credential_manager_both_env_and_file(mock_home_dir_api_key, mock_env_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=False)


def test_credential_manager_get_key_only_env_interactive(
    mock_home_dir_no_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=True)


def test_credential_manager_get_key_only_file_interactive(
    mock_home_dir_api_key, mock_env_missing
):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key(interactive=True)


def test_credential_manager_both_env_and_file_interactive(
    mock_home_dir_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=True)


def test_credential_manager_write_to_file_empty_impact_dir_exists(
    mock_home_dir_with_empty_impact_dir,
):
    cred_manager = CredentialManager()
    cred_manager.write_key_to_file("a_new_api_key_2")
    assert "a_new_api_key_2" == cred_manager.get_key_from_file()


posix_only = pytest.mark.skipif(
    os.name != "posix", reason="file permission bits are POSIX-specific"
)


@pytest.fixture
def permissive_umask():
    previous = os.umask(0o022)
    yield
    os.umask(previous)


def _mode(path):
    return os.stat(path).st_mode & 0o777


@posix_only
def test_write_to_file_creates_key_readable_only_by_owner(
    mock_home_dir_no_api_key, permissive_umask
):
    # Given no key file and a umask that would make new files world-readable
    cred_manager = CredentialManager()

    # When the key is written
    cred_manager.write_key_to_file("a_new_api_key")

    # Then only the owner can access the key file and its directory
    key_file = cred_manager._cred_file()
    assert _mode(key_file) == 0o600
    assert _mode(os.path.dirname(key_file)) == 0o700


@posix_only
def test_write_to_file_restricts_existing_world_readable_key(
    mock_home_dir_api_key, permissive_umask
):
    # Given a key file left world-readable by an earlier version
    cred_manager = CredentialManager()
    key_file = cred_manager._cred_file()
    os.chmod(key_file, 0o644)

    # When the key is written again
    cred_manager.write_key_to_file("a_new_api_key")

    # Then the key file is restricted to the owner and holds the new key
    assert _mode(key_file) == 0o600
    assert cred_manager.get_key_from_file() == "a_new_api_key"


@posix_only
def test_read_from_file_restricts_world_readable_key(
    mock_home_dir_api_key, permissive_umask
):
    # Given a key file left world-readable by an earlier version
    cred_manager = CredentialManager()
    key_file = cred_manager._cred_file()
    os.chmod(key_file, 0o644)

    # When the key is read
    api_key = cred_manager.get_key_from_file()

    # Then the key is returned and the file is restricted to the owner
    assert api_key == "api_key_from_file"
    assert _mode(key_file) == 0o600


def test_write_to_file_warns_that_key_is_stored_in_plain_text(
    mock_home_dir_no_api_key, capsys
):
    # Given no key file
    cred_manager = CredentialManager()

    # When the key is written
    cred_manager.write_key_to_file("a_new_api_key")

    # Then the console names the file and the environment variable to use instead
    output = capsys.readouterr().out
    assert "plain text" in output
    assert cred_manager._cred_file() in output
    assert "MODELON_IMPACT_CLIENT_API_KEY" in output


@posix_only
def test_read_from_file_fails_when_world_readable_key_cannot_be_restricted(
    mock_home_dir_api_key, monkeypatch
):
    # Given a world-readable key file whose permissions cannot be changed
    cred_manager = CredentialManager()
    key_file = cred_manager._cred_file()
    os.chmod(key_file, 0o644)

    def chmod_not_permitted(path, mode):
        raise PermissionError(path)

    monkeypatch.setattr(os, "chmod", chmod_not_permitted)

    # When the key is read
    # Then reading fails with an error naming the file
    with pytest.raises(InsecureCredentialsFileError, match=re.escape(key_file)):
        cred_manager.get_key_from_file()
