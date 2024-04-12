"""
conftest.py
"""
import collections
import json
import os
import re
from glob import glob

import pytest
import requests
import requests_mock

from tests.impact.client.helpers import IDs, with_json_route

MockedServer = collections.namedtuple("MockedServer", ["url", "context", "adapter"])


def py_file_path_to_module_path(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    py_file_path_to_module_path(fixture)
    for fixture in glob("tests/impact/client/fixtures/*.py")
    if "__" not in fixture
]


def extract_email(input_string):
    # Define a regular expression pattern for extracting email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    # Use re.findall to find all email addresses in the input string
    emails = re.findall(email_pattern, input_string)

    return emails


class MockContex:
    def __init__(self, session):
        self.session = session


@pytest.fixture
def mock_server_base():
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount("http://", adapter)
    mock_url = "http://mock-impact.com"

    mock_server_base = MockedServer(mock_url, MockContex(session), adapter)
    mock_server = with_json_route(mock_server_base, "POST", "api/login", {})
    mock_server = with_json_route(
        mock_server,
        "GET",
        "hub/api/",
        {},
        extra_headers={},
    )
    return mock_server


def keep_only_keys(dictionary, keys_to_keep):
    """
    Remove all keys from dictionary except those specified in keys_to_keep list.

    Parameters:
        dictionary (dict): The input dictionary.
        keys_to_keep (list): List of keys to keep.

    Returns:
        dict: Dictionary with only specified keys.
    """
    return {key: dictionary[key] for key in keys_to_keep if key in dictionary}


@pytest.fixture(scope="module")
def vcr_config():
    def scrub_request(request):
        # Scrub off JH token
        if "/hub/api/authorizations/token" in request.path:
            token = request.path.split("/")[-1]
            request.uri = request.path.replace(token, "dummy")
        extracted_emails = extract_email(request.path)

        url = os.environ.get("MODELON_IMPACT_CLIENT_URL")
        if url is not None:
            request.uri = request.path.replace(url, IDs.MOCK_IMPACT_URL)

        # Scrub username assuming username is an email always
        if extracted_emails:
            request.uri = request.path.replace(extracted_emails[0], IDs.MOCK_EMAIL)

        return request

    def scrub_content_before_response_record(response):
        if response:
            # Scrubbing off headers that are not relevant or contain cookies
            headers_to_exclude = [
                "set-cookie",
                "content-security-policy",
                "etag",
                "Strict-Transport-Security",
                "Date",
                "Content-Length",
            ]
            for header in headers_to_exclude:
                response["headers"].pop(header, None)
            username = os.environ.get("MODELON_IMPACT_USERNAME")
            if response.get("body", {}).get("string"):
                try:
                    body = response["body"]["string"].decode("utf-8")
                    if username:
                        insensitive_username = re.compile(
                            re.escape(username), re.IGNORECASE
                        )
                        body = insensitive_username.sub(IDs.MOCK_EMAIL, body)
                    response_body = json.loads(body)
                except UnicodeDecodeError:
                    # Handle case where response is not json
                    return response
                # Return response as it is if its a list(To handle trajectories api)
                if isinstance(response_body, list):
                    return response
                # Scrubbing off response from users/me
                elif response_body.get("data", {}).get("encryptionKey"):
                    response_body["data"] = keep_only_keys(
                        response_body["data"], ["license", "username"]
                    )
                # Scrub off response from /hub/api/authorizations/token/<token>
                elif response_body.get("last_activity"):
                    response_body = keep_only_keys(response_body, ["name", "server"])
                # Scrub off response from /api/login
                elif response_body.get("identifier"):
                    response_body.pop("identifier", None)
                response["body"]["string"] = json.dumps(response_body).encode()
        return response

    return {
        "record_mode": "once",
        "filter_headers": ["authorization", "Cookie", "User-Agent"],  # Scrub off tokens
        "filter_post_data_parameters": ["secretKey"],  # Scrub off MI API key
        "before_record_request": scrub_request,
        "before_record_response": scrub_content_before_response_record,
        "decode_compressed_response": True,
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    # Put all cassettes in vhs/{module}/{test}.yaml
    path_split = request.module.__name__.split(".")
    return os.path.join("tests/fixtures/vcr_cassettes", path_split[-1])
