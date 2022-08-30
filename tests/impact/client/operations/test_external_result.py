import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import create_external_result_entity
from modelon.impact.client.operations.base import AsyncOperationStatus
from modelon.impact.client.operations.external_result import (
    ExternalResultUploadOperation,
)
from tests.impact.client.fixtures import *


class TestExternalResultUploadOperation:
    def test_given_running_when_wait_then_timeout(
        self, workspace_sal_upload_result_running
    ):
        # Given
        workspace_service = workspace_sal_upload_result_running
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When, then
        pytest.raises(exceptions.OperationTimeOutError, upload_op.wait, 1)

    def test_given_ready_when_wait_then_ok(self, workspace_sal_upload_result_ready):
        # Given
        workspace_service = workspace_sal_upload_result_ready
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When
        result = upload_op.wait()

        # Then
        assert isinstance(upload_op, ExternalResultUploadOperation)
        assert upload_op.id == '2f036b9fab6f45c788cc466da327cc78workspace'
        assert upload_op.status() == AsyncOperationStatus.READY
        assert upload_op.status().done()
        assert result == create_external_result_entity(
            '2f036b9fab6f45c788cc466da327cc78workspace'
        )
        meta = result.metadata
        assert meta.id == "2f036b9fab6f45c788cc466da327cc78workspace"
        assert meta.name == "result_for_PID"
        assert meta.description == "This is a result file for PID controller"
        assert meta.workspace_id == IDs.WORKSPACE_PRIMARY
        assert result.id == "2f036b9fab6f45c788cc466da327cc78workspace"

    def test_give_status_ready_when_cancel_then_raises_not_implemented(
        self, workspace_sal_upload_result_ready
    ):
        # Given
        workspace_service = workspace_sal_upload_result_ready
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When, then
        pytest.raises(NotImplementedError, upload_op.cancel)
