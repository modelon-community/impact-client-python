import pytest
import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.exceptions

from tests.impact.client.fixtures import *


class TestService:
    def test_api_get_metadata(self, api_get_metadata):
        uri = URI(api_get_metadata.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=api_get_metadata.context
        )
        data = service.api_get_metadata()
        assert data == {'version': '1.1.0'}

    def test_given_no_error_when_access_then_no_login_and_ok(self, create_workspace):
        # Given
        uri = URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        service.add_login_retry_with(api_key=None)

        # when
        data = service.workspace.workspace_create('AwesomeWorkspace')

        # Then
        assert len(create_workspace.adapter.request_history) == 1
        assert data == {'id': 'newWorkspace'}

    def test_given_authenticat_fail_once_when_access_then_login_and_ok(
        self, create_workspace_fail_auth_once
    ):
        # Given
        uri = URI(create_workspace_fail_auth_once.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace_fail_auth_once.context
        )
        service.add_login_retry_with(api_key=None)

        # When
        data = service.workspace.workspace_create('AwesomeWorkspace')

        # Then
        assert len(create_workspace_fail_auth_once.adapter.request_history) == 3
        assert data == {'id': 'newWorkspace'}

    def test_given_authenticat_fail_many_when_access_then_fail(
        self, create_workspace_fail_auth_many
    ):
        # Given
        uri = URI(create_workspace_fail_auth_many.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace_fail_auth_many.context
        )
        service.add_login_retry_with(api_key=None)

        # When
        with pytest.raises(modelon.impact.client.sal.exceptions.HTTPError):
            service.workspace.workspace_create('AwesomeWorkspace')

        # Then
        assert len(create_workspace_fail_auth_many.adapter.request_history) == 3

    def test_given_non_auth_failure_when_access_then_fail(
        self, create_workspace_fail_bad_input
    ):
        # Given
        uri = URI(create_workspace_fail_bad_input.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace_fail_bad_input.context
        )
        service.add_login_retry_with(api_key=None)

        # When
        with pytest.raises(modelon.impact.client.sal.exceptions.HTTPError):
            service.workspace.workspace_create('AwesomeWorkspace')

        # Then
        assert len(create_workspace_fail_bad_input.adapter.request_history) == 1

