"""Parse allowlisted references only. This module never performs I/O."""
import re
from urllib.parse import unquote, urlsplit, urlunsplit

from app.domain.models import AuctionHouse, AuctionReference

HOSTS = {
    "copart.com": AuctionHouse.COPART,
    "www.copart.com": AuctionHouse.COPART,
    "m.copart.com": AuctionHouse.COPART,
    "iaai.com": AuctionHouse.IAAI,
    "www.iaai.com": AuctionHouse.IAAI,
    "m.iaai.com": AuctionHouse.IAAI,
}
COPART_PATH = re.compile(r"/(?:[a-z]{2}/)?lot/([0-9]+)(?:/[A-Za-z0-9_-]+)?/?", re.IGNORECASE)
IAAI_PATH = re.compile(r"/(?:[a-z]{2}(?:-[a-z]{2})?/)?VehicleDetail/([A-Za-z0-9-]+)(?:~([A-Za-z]{2}))?/?", re.IGNORECASE)


class InvalidAuctionURL(ValueError):
    pass


def parse_auction_url(value: str) -> AuctionReference:
    # Reject parser ambiguities before urlsplit can silently strip control bytes.
    if value != value.strip() or re.search(r"[\s\\\x00-\x1f\x7f]", value):
        raise InvalidAuctionURL("URL must not contain whitespace, controls, or backslashes.")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise InvalidAuctionURL("Malformed auction URL.") from exc
    if parsed.scheme.lower() != "https":
        raise InvalidAuctionURL("Use an HTTPS Copart or IAAI listing URL.")
    if parsed.username is not None or parsed.password is not None:
        raise InvalidAuctionURL("URLs containing credentials are not accepted.")
    if host not in HOSTS or port not in (None, 443):
        raise InvalidAuctionURL("Only approved Copart and IAAI hosts on HTTPS port 443 are supported.")
    # Encoded path separators/characters create alternate route interpretations.
    if unquote(parsed.path) != parsed.path:
        raise InvalidAuctionURL("Encoded listing paths are not supported.")
    house = HOSTS[host]
    pattern = COPART_PATH if house == AuctionHouse.COPART else IAAI_PATH
    match = pattern.fullmatch(parsed.path)
    if not match:
        raise InvalidAuctionURL("URL must identify a supported lot or VehicleDetail page.")
    # Tracking parameters and fragments never participate in identity or provider lookup.
    url = urlunsplit(("https", host, parsed.path.rstrip("/"), "", ""))
    if house == AuctionHouse.COPART:
        return AuctionReference(house=house, url=url, lot_number=match.group(1))
    return AuctionReference(house=house, url=url, page_id=match.group(1))
