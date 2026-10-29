"""Bounded direct loopback-only Ollama HTTP transport; never uses proxy settings."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

BASE_URL = "http://127.0.0.1:11434"
MAX_RESPONSE_BYTES = 1024 * 1024
ALLOWED_OPERATIONS = {("GET", "/api/tags"), ("POST", "/api/show"), ("POST", "/api/chat")}


class RuntimeFailure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OllamaRuntime:
    def request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        if (method, path) not in ALLOWED_OPERATIONS:
            raise RuntimeFailure("INVALID_OPERATION", "Unsupported local-runtime operation.")
        data = json.dumps(payload, allow_nan=False).encode() if payload is not None else None
        request = Request(BASE_URL + path, data=data, method=method,
                          headers={"Content-Type": "application/json", "Accept": "application/json"})
        opener = build_opener(ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=180 if path == "/api/chat" else 5) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise RuntimeFailure("RESPONSE_TOO_LARGE", "The local model response exceeded its size limit.")
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise RuntimeFailure("INVALID_RUNTIME_RESPONSE", "The local runtime returned an invalid response.")
                return value
        except RuntimeFailure:
            raise
        except HTTPError as exc:
            raise RuntimeFailure("RUNTIME_HTTP_ERROR", "The local runtime could not complete this operation.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeFailure("RUNTIME_UNAVAILABLE", "The local Ollama service is unavailable or timed out.") from exc
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise RuntimeFailure("INVALID_RUNTIME_RESPONSE", "The local runtime returned an invalid response.") from exc
