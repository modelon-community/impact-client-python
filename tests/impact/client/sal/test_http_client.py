import pytest
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions


class TestHTTPClient:
    def test_get_json_error(self, get_with_error):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_with_error.context
        )
        pytest.raises(
            modelon.impact.client.sal.exceptions.HTTPError,
            client.get_json,
            get_with_error.url,
        )

    def test_get_json_ok(self, get_ok_empty_json):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_ok_empty_json.context
        )
        data = client.get_json(get_ok_empty_json.url)
        assert data == {}

    def test_ssl_error_mapping(self, get_with_ssl_exception):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_with_ssl_exception.context
        )
        pytest.raises(
            modelon.impact.client.sal.exceptions.SSLError,
            client.get_json,
            get_with_ssl_exception.url,
        )
