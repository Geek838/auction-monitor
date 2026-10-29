"""VIN enrichment uses one public HTTPS source with bounded, nonredirecting I/O."""
from urllib.error import URLError

import pytest

from app.vin_lookup import runtime

VIN = '1HGCM82633A004352'


class Reply:
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit):
        assert limit == runtime.MAX_RESPONSE_BYTES + 1
        return self.body[:limit]


def test_vpic_transport_uses_fixed_https_operation_no_auth_no_redirects_and_finite_timeout(monkeypatch):
    captured = {}
    class Opener:
        def open(self, request, timeout):
            captured.update(url=request.full_url, timeout=timeout, headers=dict(request.header_items()))
            return Reply(b'{"Count":1,"Results":[]}')
    def opener(*handlers):
        redirect = next(item for item in handlers if isinstance(item, runtime.NoRedirect))
        assert redirect.redirect_request(None, None, 302, None, None, 'http://169.254.169.254/') is None
        return Opener()
    monkeypatch.setattr(runtime, 'build_opener', opener)
    assert runtime.VpicClient().request_json(VIN)['Count'] == 1
    assert captured['url'] == f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json'
    assert captured['timeout'] == 10
    assert not any(key.lower() in {'authorization', 'cookie'} for key in captured['headers'])


@pytest.mark.parametrize('body,code', [(b'x' * (runtime.MAX_RESPONSE_BYTES + 1), 'RESPONSE_TOO_LARGE'), (b'not JSON', 'INVALID_RESPONSE'), (b'[]', 'INVALID_RESPONSE'), (b'[' * 2000 + b']' * 2000, 'INVALID_RESPONSE')])
def test_oversized_invalid_and_deeply_nested_source_responses_are_sanitized(monkeypatch, body, code):
    class Opener:
        def open(self, request, timeout): return Reply(body)
    monkeypatch.setattr(runtime, 'build_opener', lambda *handlers: Opener())
    with pytest.raises(runtime.VinSourceFailure) as error:
        runtime.VpicClient().request_json(VIN)
    assert error.value.code == code


@pytest.mark.parametrize('vin', ['http://evil.test/', '../admin', '1HGCM82633A00435I'])
def test_transport_direct_call_cannot_change_destination_with_a_non_vin(monkeypatch, vin):
    def unexpected(*args, **kwargs): raise AssertionError('invalid VIN opened transport')
    monkeypatch.setattr(runtime, 'build_opener', unexpected)
    with pytest.raises(runtime.VinSourceFailure): runtime.VpicClient().request_json(vin)


def test_network_failure_is_sanitized_without_raw_source_error_text(monkeypatch):
    class Opener:
        def open(self, request, timeout): raise URLError('private-debug-details')
    monkeypatch.setattr(runtime, 'build_opener', lambda *handlers: Opener())
    with pytest.raises(runtime.VinSourceFailure) as error: runtime.VpicClient().request_json(VIN)
    assert error.value.code == 'SOURCE_UNAVAILABLE'
    assert 'private-debug-details' not in str(error.value)
