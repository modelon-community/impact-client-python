"""
conftest.py
"""
import json
import os
import re
from urllib.parse import urlparse

import pytest
from vcr.filters import replace_post_data_parameters

from tests.impact.client.helpers import IDs


def extract_email(input_string):
    # Define a regular expression pattern for extracting email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    # Use re.findall to find all email addresses in the input string
    emails = re.findall(email_pattern, input_string)

    return emails


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


def _scrub_impact_url_from_request_path(request):
    url = os.environ.get("MODELON_IMPACT_CLIENT_URL")
    if url is not None:
        request.uri = request.path.replace(url, IDs.MOCK_IMPACT_URL)


def _scrub_email_from_request_path(request):
    extracted_emails = extract_email(request.path)
    if extracted_emails:
        request.uri = request.path.replace(extracted_emails[0], IDs.USERNAME)


def _scrub_auth_token_from_request_path(request):
    if "/hub/api/authorizations/token" in request.path:
        token = request.path.split("/")[-1]
        request.uri = request.path.replace(token, "dummy")


@pytest.fixture(scope="module")
def vcr_config():
    def scrub_request_before_record(request):
        # Scrub off JH token
        _scrub_auth_token_from_request_path(request)

        # Scrub Impact url and replace with mock
        _scrub_impact_url_from_request_path(request)

        # Scrub username assuming username is an email always
        _scrub_email_from_request_path(request)

        # Manually perform filter_post_data_parameters=[('secretKey', None)]
        try:
            replace_post_data_parameters(request, {"secretKey": None})
        except UnicodeDecodeError:
            pass
        return request

    def remove_query_characters(url):
        parsed_url = urlparse(url)
        return parsed_url.path

    def scrub_content_before_response_record(response):
        username = os.environ.get("MODELON_IMPACT_USERNAME")
        insensitive_username = re.compile(re.escape(username), re.IGNORECASE)
        if response:
            # Scrubbing off headers that are not relevant or contain cookies
            headers_to_exclude = [
                "set-cookie",
                "content-security-policy",
                "etag",
                "Strict-Transport-Security",
                "Date",
                "Content-Length",
                "Set-Cookie",
                "Via",
                "X-Kong-Upstream-Latency",
                "X-Kong-Proxy-Latency",
                "X-Kong-Request-Id",
            ]
            for header in headers_to_exclude:
                response["headers"].pop(header, None)
                # Scrub off location header for username and query params(client_id)
                if response["headers"].get("location"):
                    location = response["headers"]["location"][0]
                    new_location = insensitive_username.sub(
                        IDs.USERNAME, remove_query_characters(location)
                    )
                    response["headers"]["location"] = [new_location]

            if response.get("body", {}).get("string"):
                try:
                    body = response["body"]["string"].decode("utf-8")
                    if username:
                        insensitive_username = re.compile(
                            re.escape(username), re.IGNORECASE
                        )
                        body = insensitive_username.sub(IDs.USERNAME, body)
                    response_body = json.loads(body)
                except UnicodeDecodeError:
                    # Handle case where response is not json
                    return response
                except json.JSONDecodeError:
                    # Non json response
                    return response
                # Return response as it is if its a list(To handle trajectories api)
                if isinstance(response_body, list):
                    return response
                # Scrubbing off response from users/me
                elif response_body.get("data", {}).get("encryptionKey"):
                    response_body["data"] = {
                        "id": IDs.USER_ID,
                        "username": IDs.USERNAME,
                        "firstName": None,
                        "lastName": None,
                        "email": IDs.MOCK_EMAIL,
                        "license": IDs.PRO_LICENSE_ROLE,
                        "roles": [
                            "impact-editor",
                            "offline_access",
                            "impact-viewer",
                            "uma_authorization",
                            "default-roles-modelon",
                            IDs.PRO_LICENSE_ROLE,
                            "impact-executor",
                            "impact-workspace-publisher",
                        ],
                        "tenant": {
                            "id": IDs.TENANT_ID,
                            "groupName": IDs.GROUP_NAME,
                        },
                    }

                # Scrub off response from /hub/api/user
                elif response_body.get("last_activity"):
                    response_body = keep_only_keys(response_body, ["name", "server"])
                response["body"]["string"] = json.dumps(response_body).encode()
        return response

    return {
        "record_mode": "once",
        "filter_headers": [
            "authorization",
            "Cookie",
            "User-Agent",
            "impact-api-key",
        ],
        "before_record_request": scrub_request_before_record,
        "before_record_response": scrub_content_before_response_record,
        "decode_compressed_response": True,
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    # Put all cassettes in vhs/{module}/{test}.yaml
    path_split = request.module.__name__.split(".")
    return os.path.join("tests/fixtures/vcr_cassettes", path_split[-1])
