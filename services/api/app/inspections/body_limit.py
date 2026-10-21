"""Bound JSON request bytes before the framework parses the complete document."""
from starlette.responses import JSONResponse

MAX_JSON_BYTES = 16 * 1024
JSON_PATHS = {"/api/v1/inspections", "/api/v1/auction/resolve"}
JSON_LIMITS = {path: MAX_JSON_BYTES for path in JSON_PATHS} | {"/api/v1/manual-reviews": 32 * 1024}


class PreviewBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") not in JSON_LIMITS:
            return await self.app(scope, receive, send)
        limit = JSON_LIMITS[scope["path"].rstrip("/")]
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > limit:
                response = JSONResponse({"detail": f"Request body exceeds the {limit // 1024} KiB JSON limit."},
                    status_code=413, headers={"Cache-Control": "no-store"})
                return await response(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        replayed = False

        async def replay():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        return await self.app(scope, replay, send)
