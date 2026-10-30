"""Fixed HTTPS endpoint, no redirects, no towing data, bounded response."""
import json
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener
from app.exchange.runtime import NoRedirect, _unique_object, _reject_constant
from app.auction_fees.models import FeeRequest

SOURCE_URL = 'https://api.auctionfeescalculator.com'
MAX_RESPONSE = 128 * 1024


class FeeSourceFailure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


class FeeClient:
    def request_json(self, request: FeeRequest) -> dict:
        # The validated money string is inserted as a JSON number without a
        # binary-float conversion. All other values are constrained enums.
        fields = {'auction': request.auction, 'bidType': request.bid_type,
                  'bidPay': request.bid_pay, 'bidVehicle': request.bid_vehicle}
        if request.volume is not None:
            fields['volume'] = request.volume
        encoded = '{"bidAmount":' + request.bid_amount + ',' + json.dumps(fields, separators=(',', ':'))[1:]
        outgoing = Request(SOURCE_URL, data=encoded.encode('ascii'), method='POST', headers={
            'Accept': 'application/json', 'Content-Type': 'application/json',
            'User-Agent': 'AuctionIntelligence-FeeEstimate/0.6',
        })
        try:
            with build_opener(NoRedirect()).open(outgoing, timeout=10) as response:
                if response.status not in (200, 201):
                    raise FeeSourceFailure('SOURCE_UNAVAILABLE', 'The external estimate service did not complete the request.')
                raw = response.read(MAX_RESPONSE + 1)
                if len(raw) > MAX_RESPONSE:
                    raise FeeSourceFailure('RESPONSE_TOO_LARGE', 'The external estimate response exceeded its size limit.')
                value = json.loads(raw, parse_int=Decimal, parse_float=Decimal,
                                   parse_constant=_reject_constant, object_pairs_hook=_unique_object)
                if not isinstance(value, dict):
                    raise ValueError('Expected an object')
                return value
        except FeeSourceFailure:
            raise
        except HTTPError as exc:
            code = 'RATE_LIMITED' if exc.code == 429 else 'SOURCE_UNAVAILABLE'
            raise FeeSourceFailure(code, 'The external fee estimator is unavailable or rate limited.') from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise FeeSourceFailure('SOURCE_UNAVAILABLE', 'The external fee estimator is unavailable or timed out.') from exc
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise FeeSourceFailure('INVALID_RESPONSE', 'The external fee estimate could not be validated.') from exc
