"""Fixed official destination, bounded bytes, TLS-default opener and decimal JSON."""
from decimal import Decimal
from datetime import date
from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from app.exchange import runtime


class FakeResponse(BytesIO):
    pass


def fake_opener(monkeypatch, data=None, error=None):
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append((request, timeout))
            if error: raise error
            return FakeResponse(data)
    def build(*handlers):
        assert len(handlers) == 1 and isinstance(handlers[0], runtime.NoRedirect)
        return Opener()
    monkeypatch.setattr(runtime, 'build_opener', build)
    return calls


def test_fixed_official_url_and_native_decimal_parsing(monkeypatch):
    calls = fake_opener(monkeypatch, b'[{"rate":2.5959,"quantity":1}]')
    result = runtime.NbgClient(date(2026, 10, 31)).request_json()
    assert result[0]['rate'] == Decimal('2.5959') and type(result[0]['rate']) is Decimal
    request, timeout = calls[0]
    assert request.full_url == runtime.SOURCE_URL + '/?date=2026-10-31'
    assert request.full_url.startswith('https://nbg.gov.ge/')
    assert timeout == 10 and request.get_method() == 'GET'


def test_redirect_handler_declines_even_same_host_redirects():
    assert runtime.NoRedirect().redirect_request(None, None, 302, 'moved', {}, 'http://127.0.0.1/admin') is None


@pytest.mark.parametrize('body', [b'{}', b'not-json', b'[{"rate":NaN}]', b'[{"rate":Infinity}]', b'[{"rate":1,"rate":2}]', b'\xff', b'[' * 2000])
def test_invalid_or_ambiguous_json_is_sanitized(monkeypatch, body):
    fake_opener(monkeypatch, body)
    with pytest.raises(runtime.ExchangeSourceFailure) as exc:
        runtime.NbgClient().request_json()
    assert exc.value.code == 'INVALID_RESPONSE'


def test_response_limit(monkeypatch):
    fake_opener(monkeypatch, b' ' * (runtime.MAX_RESPONSE_BYTES + 1))
    with pytest.raises(runtime.ExchangeSourceFailure) as exc:
        runtime.NbgClient().request_json()
    assert exc.value.code == 'RESPONSE_TOO_LARGE'


@pytest.mark.parametrize('error', [TimeoutError('secret'), URLError('secret'), OSError('secret'),
    HTTPError(runtime.SOURCE_URL, 302, 'redirect', {}, None), HTTPError(runtime.SOURCE_URL, 429, 'limit', {}, None)])
def test_transport_errors_do_not_leak_internal_details(monkeypatch, error):
    fake_opener(monkeypatch, error=error)
    with pytest.raises(runtime.ExchangeSourceFailure) as exc:
        runtime.NbgClient().request_json()
    assert exc.value.code == 'SOURCE_UNAVAILABLE'
    assert 'secret' not in exc.value.message
