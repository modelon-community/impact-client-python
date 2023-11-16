import unittest.mock as mock

import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import IDs


class TestExternalResultService:
    def test_result_upload(self, upload_result):
        uri = URI(upload_result.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.external_result.result_upload(
                IDs.WORKSPACE_PRIMARY, "test.mat"
            )
            mock_file.assert_called_with("test.mat", "rb")

        assert data == {"data": {"location": f"api/uploads/results/{IDs.IMPORT}"}}

    def test_result_upload_status(self, upload_result_status_ready):
        uri = URI(upload_result_status_ready.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_status_ready.context
        )
        resource_uri = f"api/uploads/results/{IDs.IMPORT}"
        data = service.imports.get_import_status(resource_uri)
        assert data == {
            "data": {
                "id": IDs.IMPORT,
                "status": "ready",
                "data": {"resourceUri": f"api/external-result/{IDs.EXTERNAL_RESULT}"},
            }
        }

    def test_result_upload_meta(self, upload_result_meta):
        uri = URI(upload_result_meta.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_meta.context
        )
        data = service.external_result.get_uploaded_result(IDs.EXTERNAL_RESULT)

        assert data == {
            "data": {
                "id": IDs.EXTERNAL_RESULT,
                "createdAt": "2021-09-02T08:26:49.612000",
                "name": "result_for_PID",
                "description": "This is a result file for PID controller",
                "workspaceId": IDs.WORKSPACE_PRIMARY,
            }
        }

    def test_delete_result_upload(self, upload_result_delete):
        uri = URI(upload_result_delete.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_delete.context
        )
        service.external_result.delete_uploaded_result(IDs.EXTERNAL_RESULT)
        assert upload_result_delete.adapter.called
