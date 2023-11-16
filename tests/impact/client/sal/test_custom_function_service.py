import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import IDs


class TestCustomFunctionService:
    def test_get_custom_function(self, get_custom_function):
        uri = URI(get_custom_function.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function.context
        )
        data = service.custom_function.custom_function_get(
            IDs.WORKSPACE_PRIMARY, 'cust_func'
        )
        assert data == {'name': 'cust_func', 'version': '0.0.1'}

    def test_get_custom_functions(self, get_custom_functions):
        uri = URI(get_custom_functions.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_functions.context
        )
        data = service.custom_function.custom_functions_get(IDs.WORKSPACE_PRIMARY)
        assert data == {"data": {"items": []}}

    def test_get_custom_function_default_options(
        self, get_custom_function_default_options
    ):
        uri = URI(get_custom_function_default_options.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function_default_options.context
        )
        data = service.custom_function.custom_function_default_options_get(
            IDs.WORKSPACE_PRIMARY, 'cust_func'
        )
        assert data == {'compiler': {'c_compiler': 'gcc'}}

    def test_get_custom_function_options(self, get_custom_function_options):
        uri = URI(get_custom_function_options.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function_options.context
        )
        data = service.custom_function.custom_function_options_get(
            IDs.WORKSPACE_PRIMARY, 'cust_func'
        )
        assert data == {"compiler": {"generate_html_diagnostics": True}}
