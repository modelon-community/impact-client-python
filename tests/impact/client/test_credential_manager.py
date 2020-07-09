import os
import pytest
import unittest.mock

from modelon.impact.client.credential_manager import CredentialManager


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

    def mockreturn(path):
        return str(home)

    monkeypatch.setattr(os.path, 'expanduser', mockreturn)


@pytest.fixture
def mock_home_dir_no_api_key(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    def mockreturn(path):
        return str(home)

    monkeypatch.setattr(os.path, 'expanduser', mockreturn)


def test_credential_manager_from_env_defined(mock_env_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key_from_env()


def test_credential_manager_from_env_not_defined(mock_env_missing):
    cred_manager = CredentialManager()
    assert cred_manager.get_key_from_env() is None


def test_credentail_manager_from_file(mock_home_dir_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key_from_file()


def test_credentail_manager_from_file_does_not_exist(mock_home_dir_no_api_key):
    cred_manager = CredentialManager()
    assert cred_manager.get_key_from_file() is None


def test_credentail_manager_write_to_file(mock_home_dir_no_api_key):
    cred_manager = CredentialManager()
    cred_manager.write_key_to_file("a_new_api_key")
    assert "a_new_api_key" == cred_manager.get_key_from_file()


@unittest.mock.patch("modelon.impact.client.credential_manager.getpass")
def test_credentail_manager_from_getpass(getpass):
    getpass.return_value = "api_key_from_getpass"
    cred_manager = CredentialManager()
    assert "api_key_from_getpass" == cred_manager.get_key_from_prompt()


def test_credentail_manager_get_key_nothing(mock_home_dir_no_api_key, mock_env_missing):
    cred_manager = CredentialManager()
    assert cred_manager.get_key(interactive=False) is None


@unittest.mock.patch("modelon.impact.client.credential_manager.getpass")
def test_credentail_manager_get_key_interactive(
    getpass, mock_home_dir_no_api_key, mock_env_missing
):
    getpass.return_value = "api_key_from_getpass"
    cred_manager = CredentialManager()
    assert "api_key_from_getpass" == cred_manager.get_key(interactive=True)


def test_credentail_manager_get_key_only_env(
    mock_home_dir_no_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=False)


def test_credentail_manager_get_key_only_file(mock_home_dir_api_key, mock_env_missing):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key(interactive=False)


def test_credentail_manager_both_env_and_file(mock_home_dir_api_key, mock_env_api_key):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=False)


def test_credentail_manager_get_key_only_env_interactive(
    mock_home_dir_no_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=True)


def test_credentail_manager_get_key_only_file_interactive(
    mock_home_dir_api_key, mock_env_missing
):
    cred_manager = CredentialManager()
    assert "api_key_from_file" == cred_manager.get_key(interactive=True)


def test_credentail_manager_both_env_and_file_interactive(
    mock_home_dir_api_key, mock_env_api_key
):
    cred_manager = CredentialManager()
    assert "api_key_from_env" == cred_manager.get_key(interactive=True)
