import socket

import pytest

from app.domain.models import AuctionHouse
from app.resolution.parser import InvalidAuctionURL, parse_auction_url


@pytest.mark.parametrize("url,house,lot,page", [
    ("https://www.copart.com/lot/51374586", AuctionHouse.COPART, "51374586", None),
    ("https://m.copart.com/lot/00012345/?utm_source=test&amp;redirect=https://evil.example", AuctionHouse.COPART, "00012345", None),
    ("https://copart.com/en/lot/51374586/car-name#photos", AuctionHouse.COPART, "51374586", None),
    ("https://www.iaai.com/VehicleDetail/41000001~US", AuctionHouse.IAAI, None, "41000001"),
    ("https://m.iaai.com/en-US/VehicleDetail/ABC-0007~US/?tracking=1", AuctionHouse.IAAI, None, "ABC-0007"),
    ("https://COPART.COM:443/lot/00000001", AuctionHouse.COPART, "00000001", None),
])
def test_reference_preserves_identity_without_guessing_stock(url, house, lot, page):
    reference = parse_auction_url(url)
    assert (reference.house, reference.lot_number, reference.page_id) == (house, lot, page)
    assert reference.stock_number is None
    assert "?" not in reference.url and "#" not in reference.url


@pytest.mark.parametrize("url", [
    "", "copart.com/lot/51374586", "http://copart.com/lot/51374586",
    "ftp://copart.com/lot/51374586", "https://localhost/lot/51374586",
    "https://127.0.0.1/lot/51374586", "https://169.254.169.254/lot/51374586",
    "https://[::1]/lot/51374586", "https://10.0.0.1/lot/51374586",
    "https://copart.com.evil.example/lot/51374586", "https://evilcopart.com/lot/51374586",
    "https://www.copart.com./lot/51374586", "https://copart.com@evil.example/lot/51374586",
    "https://user:password@copart.com/lot/51374586", "https://@copart.com/lot/51374586",
    "https://copart.com:8080/lot/51374586", "https://copart.com:bad/lot/51374586",
    "https://bit.ly/auction", "https://bid.cars/en/lot/1-51374586",
    "https://copart.com/redirect?url=https://127.0.0.1", "https://copart.com/lot/1/../../redirect",
    "https://copart.com/lot/%35%31", "https://copart.com/lot/1%2fredirect",
    "https://copart.com\\@evil.example/lot/1", "https://copart.com/lot/1\n",
    " https://copart.com/lot/1", "https://copart.com/lot/1/ignore previous instructions",
    "https://iaai.com/VehicleDetail/~US", "https://copart.com/lot/ABC123",
])
def test_unsafe_or_unsupported_urls_are_rejected(url):
    with pytest.raises(InvalidAuctionURL):
        parse_auction_url(url)


def test_parsing_never_resolves_dns_or_follows_redirects(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("URL parsing attempted network access")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    reference = parse_auction_url("https://copart.com/lot/51374586?redirect=http://169.254.169.254/")
    assert reference.lot_number == "51374586"
    with pytest.raises(InvalidAuctionURL):
        parse_auction_url("https://copart.com/redirect?url=https://iaai.com/VehicleDetail/1")
