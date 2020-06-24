import logging
import requests
import urllib.parse

import modelon.impact.client.sal.exceptions


logger = logging.getLogger(__name__)


class Service:
    def __init__(self, uri, context=None):
        self._uri = URI(uri)
        self._context = context if context else Context()

    def get(self, path, check_return=True, **kvargs):
        request = Request(self._context, "GET", self._uri.with_path(path))
        return request.execute(check_return=check_return, **kvargs)

    def post(self, path, body, check_return=True, **kwargs):
        request = Request(self._context, "POST", self._uri.with_path(path), body)
        return request.execute(check_return=check_return, **kwargs)


class URI:
    def __init__(self, content):
        self.content = content

    def with_path(self, path):
        return URI(urllib.parse.urljoin(self.content + "/", path))

    def resolve(self, **kwargs):
        return self.content.format(**kwargs)


class Request:
    def __init__(self, context, method, uri, body=None):
        self.context = context
        self.method = method
        self.uri = uri
        self.body = body

    def execute(self, check_return=True, **kwargs):
        url = self.uri.resolve(**kwargs)

        try:
            if self.method == "POST":
                logger.debug("POST with JSON body: {}".format(self.body))
                resp = self.context.session.post(url, json=self.body)
            elif self.method == "GET":
                resp = self.context.session.get(url)
            else:
                raise NotImplementedError()
        except requests.exceptions.RequestException as exce:
            raise modelon.impact.client.sal.exceptions.CommunicationException(
                "Communication when doing a request failed"
            ) from exce

        resp = Response(resp)
        if check_return and not resp.ok:
            raise modelon.impact.client.sal.exceptions.HTTPError(resp.error.message)

        return resp


class Context:
    def __init__(self):
        self.session = requests.Session()


class Response:
    def __init__(self, resp_obj):
        self._resp_obj = resp_obj

    def _is_json(self):
        return 'application/json' in self._resp_obj.headers.get('content-type')

    @property
    def data(self):
        if not self._resp_obj.ok:
            raise modelon.impact.client.sal.exceptions.HTTPError(self.error.message)

        if not self._is_json():
            raise ValueError('This request does not return any data/json')

        return self._resp_obj.json()

    @property
    def status_code(self):
        return self._resp_obj.status_code

    @property
    def ok(self):
        return self._resp_obj.ok

    @property
    def error(self):
        if self._resp_obj.ok:
            raise ValueError('This request was successfull!')

        # TODO: Should this throw exception or do we map to a different ResponseError?
        if not self._is_json():
            raise Exception('Unknown error, body: ' + str(self._resp_obj.content))

        json = self._resp_obj.json()
        if 'error' not in json:
            raise Exception('Unknown error, json body: ' + str(self._resp_obj.content))

        error = json['error']
        return ResponseError(error['message'], error['code'])


class ResponseError:
    def __init__(self, message, code):
        self.message = message
        self.code = code
