"""The optional local runtime cannot redirect pixels or honor proxy settings."""
from urllib.request import ProxyHandler

import pytest

from app.local_vision import runtime


class Reply:
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit):
        assert limit == runtime.MAX_RESPONSE_BYTES + 1
        return self.body[:limit]


def test_transport_is_fixed_loopback_no_proxy_no_redirect_and_bounded(monkeypatch):
    captured = {}
    class Opener:
        def open(self, request, timeout):
            captured.update(url=request.full_url, data=request.data, timeout=timeout)
            return Reply(b'{"ok":true}')
    def opener(*handlers):
        assert any(isinstance(item, ProxyHandler) and item.proxies == {} for item in handlers)
        redirect = next(item for item in handlers if isinstance(item, runtime.NoRedirect))
        assert redirect.redirect_request(None, None, 302, None, None, 'https://external.invalid/') is None
        return Opener()
    monkeypatch.setenv('HTTP_PROXY', 'http://external.invalid:8080')
    monkeypatch.setattr(runtime, 'build_opener', opener)
    assert runtime.OllamaRuntime().request_json('POST', '/api/chat', {'model': 'test'}) == {'ok': True}
    assert captured['url'] == 'http://127.0.0.1:11434/api/chat'
    assert captured['timeout'] == 180
    assert b'test' in captured['data']


@pytest.mark.parametrize('method,path', [('GET', 'https://external.invalid/'), ('POST', '/api/pull'), ('GET', '/api/chat'), ('POST', '/../admin')])
def test_unlisted_operations_fail_before_opening_a_connection(method, path, monkeypatch):
    def unexpected(*args, **kwargs): raise AssertionError('unlisted operation opened transport')
    monkeypatch.setattr(runtime, 'build_opener', unexpected)
    with pytest.raises(runtime.RuntimeFailure, match='Unsupported'):
        runtime.OllamaRuntime().request_json(method, path)


@pytest.mark.parametrize('body,code', [(b'x' * (runtime.MAX_RESPONSE_BYTES + 1), 'RESPONSE_TOO_LARGE'), (b'not JSON', 'INVALID_RUNTIME_RESPONSE'), (b'[]', 'INVALID_RUNTIME_RESPONSE')])
def test_oversized_and_invalid_runtime_responses_fail_closed(body, code, monkeypatch):
    class Opener:
        def open(self, request, timeout): return Reply(body)
    monkeypatch.setattr(runtime, 'build_opener', lambda *handlers: Opener())
    with pytest.raises(runtime.RuntimeFailure) as error:
        runtime.OllamaRuntime().request_json('GET', '/api/tags')
    assert error.value.code == code
