import asyncio

from app.inspections.body_limit import MAX_JSON_BYTES, PreviewBodyLimit


def exercise(chunks):
    calls = []
    sent = []
    incoming = iter({"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
                    for index, chunk in enumerate(chunks))

    async def receive():
        return next(incoming)

    async def send(message):
        sent.append(message)

    async def application(scope, replay, send_response):
        calls.append(await replay())
        await send_response({"type": "http.response.start", "status": 200, "headers": []})
        await send_response({"type": "http.response.body", "body": b"ok"})

    scope = {"type": "http", "method": "POST", "path": "/api/v1/inspections", "headers": []}
    asyncio.run(PreviewBodyLimit(application)(scope, receive, send))
    return calls, sent


def test_chunked_body_cannot_bypass_limit_when_content_length_is_absent():
    calls, sent = exercise([b"x" * (MAX_JSON_BYTES // 2), b"y" * (MAX_JSON_BYTES // 2 + 1)])
    assert calls == []
    assert next(item["status"] for item in sent if item["type"] == "http.response.start") == 413


def test_bounded_chunked_json_is_replayed_intact_to_the_framework():
    first, second = b'{"url":', b'"https://copart.com/lot/51374586"}'
    calls, sent = exercise([first, second])
    assert calls == [{"type": "http.request", "body": first + second, "more_body": False}]
    assert next(item["status"] for item in sent if item["type"] == "http.response.start") == 200
