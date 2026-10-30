"""Optional Apibara URL lookup; metadata only, no photo or live-feed claims."""
import asyncio
from datetime import datetime, timezone
import json
import os
import re
from threading import BoundedSemaphore
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener

from app.domain.models import (AuctionHouse, AuctionReference, FieldEvidence, ListingIdentity,
                               Provenance, ProviderResolution, Vehicle, VehicleSnapshot)
from app.exchange.runtime import NoRedirect, _reject_constant, _unique_object
from app.providers.base import NotAuthorized, SourceUnavailable
from app.resolution.parser import InvalidAuctionURL, parse_auction_url

ENDPOINT = 'https://apibara.tech/api/v1/vehicle-auction/vehicles/urltodetails'
MAX_RESPONSE_BYTES = 1024 * 1024
SLOTS = BoundedSemaphore(2)


def _text(value, name, *, max_length=200):
    if value is None or value == '':
        return None
    if not isinstance(value, str) or len(value) > max_length or any(ord(c) < 32 for c in value):
        raise SourceUnavailable(f'Invalid provider {name}.')
    return value.strip() or None


def _fetch(reference: AuctionReference):
    key = os.environ.get('APIBARA_API_KEY', '')
    if not key or len(key) > 512 or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise NotAuthorized('Provider credentials are unavailable or invalid.')
    if not SLOTS.acquire(blocking=False):
        raise SourceUnavailable('Provider is busy.')
    try:
        # URL was already parsed; the canonical form strips query parameters and fragments.
        req = Request(ENDPOINT + '?' + urlencode({'url': reference.url}), headers={
            'X-API-Key': key, 'Accept': 'application/json',
            'User-Agent': 'AuctionIntelligence-Apibara/0.1',
        })
        try:
            with build_opener(NoRedirect()).open(req, timeout=15) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise SourceUnavailable('Provider response exceeds its size limit.')
                result = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
                if not isinstance(result, dict) or not isinstance(result.get('data'), dict):
                    raise SourceUnavailable('Provider response lacks a vehicle record.')
                return result['data']
        except HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code in (401, 403):
                raise NotAuthorized('Provider rejected credentials or access.') from exc
            raise SourceUnavailable('Provider could not complete lookup.') from exc
        except (URLError, TimeoutError, OSError, ValueError, UnicodeError, RecursionError) as exc:
            raise SourceUnavailable('Provider could not complete lookup.') from exc
    finally:
        SLOTS.release()


class ApibaraProvider:
    warnings = [
        'Apibara metadata is third-party information; provider rights, coverage and freshness have not been independently verified.',
        'The selected listing URL is sent to Apibara. No photos are fetched or displayed.',
    ]

    async def resolve(self, reference: AuctionReference) -> ProviderResolution:
        try:
            parsed = parse_auction_url(reference.url)
        except InvalidAuctionURL as exc:
            raise SourceUnavailable('Invalid auction reference.') from exc
        if parsed != reference:
            raise SourceUnavailable('Auction reference does not match its parsed URL.')
        # The documented endpoint supplies no independent page-to-stock proof.
        # Do not spend a request or infer an IAAI stock number from its page ID.
        if parsed.house == AuctionHouse.IAAI:
            return ProviderResolution()
        expected = ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number=parsed.lot_number)
        raw = await asyncio.to_thread(_fetch, parsed)
        if raw is None:
            return ProviderResolution(identity=expected)
        platform = _text(raw.get('platform'), 'platform', max_length=16)
        lot = _text(raw.get('lot_number'), 'lot number', max_length=64)
        if not platform or platform.casefold() not in {'copart', 'iaai'} or not lot or not re.fullmatch(r'[A-Za-z0-9-]+', lot):
            raise SourceUnavailable('Provider did not supply a usable auction identity.')
        house = AuctionHouse(platform.upper())
        identity = ListingIdentity(house=house, lot_or_stock_number=lot)
        vin = _text(raw.get('vin'), 'VIN', max_length=32)
        # Missing/masked VIN is not evidence of a vehicle identity.
        if vin and not re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', vin.upper()):
            vin = None
        elif vin:
            vin = vin.upper()
        year = raw.get('year')
        if year is not None and (type(year) is not int or not 1886 <= year <= datetime.now(timezone.utc).year + 2):
            raise SourceUnavailable('Provider returned an invalid model year.')
        vehicle = Vehicle(vin=vin, year=year, make=_text(raw.get('make'), 'make'),
                          model=_text(raw.get('model'), 'model'), primary_damage=_text(raw.get('damage'), 'damage'))
        now = datetime.now(timezone.utc)
        record_id = f'apibara:{house.value}:{lot}'
        snapshot = VehicleSnapshot(record_id=record_id, identity=identity, vehicle=vehicle, event_status='UNKNOWN',
            provenance=Provenance(provider='APIBARA', source_name='Apibara URL lookup', source_url=parsed.url,
                retrieved_at=now, source_observed_at=None, license_scope='User enabled third-party metadata; usage rights are unverified.',
                data_type='EXTERNAL_UNVERIFIED', realtime=False),
            field_evidence={field: FieldEvidence(kind='MISSING' if value is None else 'SUPPLIED', source='Apibara',
                note='Provider-reported; not independently verified.') for field, value in vehicle.model_dump().items()})
        return ProviderResolution(identity=expected, candidates=[snapshot])

    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot:
        raise SourceUnavailable('Independent vehicle-record retrieval is not enabled for this provider.')
