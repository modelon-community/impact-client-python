import modelon.impact.client.configuration as configuration


def test_get_client_url_default(monkeypatch):
    monkeypatch.delenv("MODELON_IMPACT_CLIENT_URL")
    assert "https://impact.modelon.cloud/" == configuration.get_client_url()


def test_get_client_url_env(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_URL", "https://impact.modelon.cloud")
    assert "https://impact.modelon.cloud" == configuration.get_client_url()


def test_get_client_interactive_default():
    assert not configuration.get_client_interactive()


def test_get_client_interactive_env_1(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_INTERACTIVE", "true")
    assert configuration.get_client_interactive()


def test_get_client_interactive_env_2(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_INTERACTIVE", "1")
    assert configuration.get_client_interactive()


def test_get_client_interactive_env_3(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_INTERACTIVE", "TrUe")
    assert configuration.get_client_interactive()


def test_get_client_interactive_env_4(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_INTERACTIVE", "false")
    assert not configuration.get_client_interactive()


def test_get_client_interactive_env_5(monkeypatch):
    monkeypatch.setenv("MODELON_IMPACT_CLIENT_INTERACTIVE", "what?")
    assert not configuration.get_client_interactive()
