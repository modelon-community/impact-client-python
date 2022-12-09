from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service


class TestWorkspaceService:
    def test_download_exported_archive(self, get_export_archive):
        uri = URI(get_export_archive.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_export_archive.context
        )
        data = service.export.export_download('api/exports/79sd8-3n2a4-e3t24')
        assert data == b'\x00\x00\x00\x00'
