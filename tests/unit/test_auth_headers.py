from aiohttp.test_utils import make_mocked_request

from yaps.utils.auth.auth_token import AuthUtils


def test_auth_headers_success():
    request = make_mocked_request('POST', "/", headers={'Authorization': 'Bearer sometoken'})
    result = AuthUtils().extract_auth_token(request)
    assert result == "sometoken"


def test_auth_headers_is_none():
    request = make_mocked_request('POST', "/", headers={})
    result = AuthUtils().extract_auth_token(request)
    assert result is None
