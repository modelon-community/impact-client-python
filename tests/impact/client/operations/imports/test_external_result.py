import pytest

from modelon.impact.client import exceptions
from tests.impact.client.helpers import create_external_result_entity, IDs
from modelon.impact.client.operations.base import AsyncOperationStatus
from modelon.impact.client.operations.external_result_import import (
    ExternalResultImportOperation,
)
from modelon.impact.client.entities.external_result import ExternalResult


class TestExternalResultImportOperation:
    def test_given_running_when_wait_then_timeout(
        self, external_result_sal_upload_running
    ):
        # Given
        upload_op = ExternalResultImportOperation[ExternalResult](
            f'api/uploads/results/{IDs.IMPORT}',
            external_result_sal_upload_running,
            ExternalResult.from_operation,
        )

        # When, then
        pytest.raises(exceptions.OperationTimeOutError, upload_op.wait, 1)

    def test_given_error_when_wait_then_upload_error(
        self, external_result_sal_upload_error
    ):
        # Given
        upload_op = ExternalResultImportOperation[ExternalResult](
            f'api/uploads/results/{IDs.IMPORT}',
            external_result_sal_upload_error,
            ExternalResult.from_operation,
        )

        # When, then
        pytest.raises(exceptions.ExternalResultUploadError, upload_op.wait, 1)

    def test_given_ready_when_wait_then_ok(self, external_result_sal_upload_ready):
        # Given
        upload_op = ExternalResultImportOperation[ExternalResult](
            f'api/uploads/results/{IDs.IMPORT}',
            external_result_sal_upload_ready,
            ExternalResult.from_operation,
        )

        # When
        result = upload_op.wait()

        # Then
        assert isinstance(upload_op, ExternalResultImportOperation)
        assert upload_op.id == IDs.IMPORT
        assert upload_op.status() == AsyncOperationStatus.READY
        assert upload_op.status().done()
        assert result == create_external_result_entity(IDs.EXTERNAL_RESULT)
        meta = result.metadata
        assert meta.id == IDs.EXTERNAL_RESULT
        assert meta.name == "result_for_PID"
        assert meta.description == "This is a result file for PID controller"
        assert meta.workspace_id == IDs.WORKSPACE_PRIMARY
        assert result.id == IDs.EXTERNAL_RESULT

    def test_give_status_ready_when_cancel_then_raises_not_implemented(
        self, external_result_sal_upload_ready
    ):
        # Given
        upload_op = ExternalResultImportOperation[ExternalResult](
            f'api/uploads/results/{IDs.IMPORT}',
            external_result_sal_upload_ready,
            ExternalResult.from_operation,
        )

        # When, then
        pytest.raises(NotImplementedError, upload_op.cancel)
