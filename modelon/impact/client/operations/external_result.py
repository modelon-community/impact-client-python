from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus


class ExternalResultUploadOperation(AsyncOperation):
    """
    An operation class for the modelon.impact.client.entities.
    external_result.ExternalResult class.
    """

    def __init__(self, result_id: str, service: Service):
        super().__init__()
        self._result_id = result_id
        self._sal = service

    def __repr__(self):
        return f"Result upload operations for id '{self._result_id}'"

    def __eq__(self, obj):
        return (
            isinstance(obj, ExternalResultUploadOperation)
            and obj._result_id == self._result_id
        )

    @property
    def id(self):
        """Result id"""
        return self._result_id

    @property
    def name(self):
        """Return the name of operation"""
        return "Result upload"

    def cancel(self):
        raise NotImplementedError('Cancel is not supported for this operation')

    def data(self):
        """
        Returns a new ExternalResult class instance.

        Returns:

            external_result --
                A ExternalResult class instance.
        """
        return ExternalResult(self._result_id, self._sal)

    def status(self):
        """
        Returns the upload status as an enumeration.

        Returns:

            upload_status --
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            workspace.upload_result('C:/A.mat').status()
        """
        return AsyncOperationStatus(
            self._sal.workspace.get_result_upload_status(self._result_id)["data"][
                "status"
            ]
        )
