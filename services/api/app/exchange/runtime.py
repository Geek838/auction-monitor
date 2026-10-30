"""Bounded official fixed-host read; no user URLs or redirects."""
import json
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

SOURCE_URL = 'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json'
MAX_RESPONSE_BYTES = 128 * 1024


class ExchangeSourceFailure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate source field')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError('Non-finite source number')


class NbgClient:
    def request_json(self) -> list:
        request = Request(SOURCE_URL, headers={
            'Accept': 'application/json', 'User-Agent': 'AuctionIntelligence-ReferenceFX/0.6',
        })
        try:
            # Preserve standard TLS validation and configured proxy policy.
            with build_opener(NoRedirect()).open(request, timeout=10) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ExchangeSourceFailure('RESPONSE_TOO_LARGE', 'Official exchange-rate response exceeded its size limit.')
                value = json.loads(raw, parse_float=Decimal, parse_constant=_reject_constant,
                                   object_pairs_hook=_unique_object)
                if not isinstance(value, list):
                    raise ValueError('Expected source list')
                return value
        except ExchangeSourceFailure:
            raise
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ExchangeSourceFailure('SOURCE_UNAVAILABLE', 'The official exchange-rate service is unavailable or timed out.') from exc
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise ExchangeSourceFailure('INVALID_RESPONSE', 'Official exchange-rate data could not be validated.') from exc
