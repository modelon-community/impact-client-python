"""Response class"""
import re
from typing import Text, Union, Dict, Any
from modelon.impact.client.sal import exceptions


class ResponseError:
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


class Response:
    def __init__(self, resp_obj):
        self._resp_obj = resp_obj

    def _is_json(self) -> bool:
        return "application/json" in self._resp_obj.headers.get("content-type")

    @property
    def status_code(self) -> int:
        return self._resp_obj.status_code

    @property
    def ok(self) -> bool:
        return self._resp_obj.ok

    @property
    def error(self) -> ResponseError:
        if self._resp_obj.ok:
            raise ValueError("This request was successfull!")

        if not self._is_json():
            raise exceptions.ErrorBodyIsNotJSONError(
                f"Error response was not JSON: {self._resp_obj.content}"
            )

        json = self._resp_obj.json()
        if "error" not in json:
            raise exceptions.ErrorJSONInvalidFormatError(
                f"Error response JSON format unknown: {self._resp_obj.content}"
            )

        error = json["error"]
        return ResponseError(error["message"], error["code"])


class JSONResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    @property
    def data(self) -> Dict[str, Any]:
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message, self._resp_obj.status_code)

        if not self._is_json():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected JSON"
            )

        return self._resp_obj.json()

    @property
    def headers(self) -> Dict[str, Any]:
        return self._resp_obj.headers


class TextResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    def _is_txt(self) -> bool:
        return "text/plain" in self._resp_obj.headers.get("content-type")

    @property
    def data(self) -> Text:
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message, self._resp_obj.status_code)

        if not self._is_txt():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected text"
            )

        return self._resp_obj.text


class ZIPResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    def _is_zip(self) -> bool:
        return "application/zip" in self._resp_obj.headers.get("content-type")

    @property
    def data(self) -> bytes:
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message, self._resp_obj.status_code)

        if not self._is_zip():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected a Binary "
                "compressed archive"
            )

        return self._resp_obj.content


class FileResponse(Response):
    def __init__(self, resp_obj, content_type: str):
        super().__init__(resp_obj)
        self.content_type = content_type

    def _is_expected_content_type(self) -> bool:
        return self.content_type in self._resp_obj.headers.get("content-type")

    @property
    def stream(self) -> Union[Text, bytes]:
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message, self._resp_obj.status_code)

        if not self._is_expected_content_type():
            raise exceptions.InvalidContentTypeError(
                f"Incorrect content type on response, expected {self.content_type}"
            )

        return (
            self._resp_obj.text
            if self.content_type.startswith("text")
            else self._resp_obj.content
        )

    @property
    def headers(self) -> Dict[str, Any]:
        return self._resp_obj.headers

    @property
    def file_name(self) -> str:
        d = self.headers["content-disposition"]
        return re.findall("filename=(.+)", d)[0].strip('"')


class CSVResponse(FileResponse):
    def __init__(self, resp_obj):
        super().__init__(resp_obj, "text/csv")


class OctetStreamResponse(FileResponse):
    def __init__(self, resp_obj):
        super().__init__(resp_obj, "application/octet-stream")


class MatStreamResponse(FileResponse):
    def __init__(self, resp_obj):
        super().__init__(resp_obj, "application/vnd.impact.mat.v1+octet-stream")
