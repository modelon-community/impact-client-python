import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import IDs


class TestWorkspaceService:
    def test_download_exported_archive(self, get_export_archive):
        uri = URI(get_export_archive.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_export_archive.context
        )
        data = service.exports.export_download(f"api/exports/{IDs.EXPORT}")
        assert data == b"\x00\x00\x00\x00"
