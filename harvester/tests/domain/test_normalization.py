from decimal import Decimal

import pytest
from expects import be_none, equal, expect

from src.domain.normalization import parse_bob_price


class ParseBobPriceTests:
    @pytest.mark.parametrize(
        ("raw_price", "expected_price"),
        [
            ("12,50", Decimal("12.50")),
            ("Bs. 12.5", Decimal("12.5")),
            ("1.250,75 Bs", Decimal("1250.75")),
            ("1,250.75", Decimal("1250.75")),
            ("1.250", Decimal("1250")),
            ("BOB 45", Decimal("45")),
        ],
    )
    def test_parses_bolivian_price_formats(self, raw_price: str, expected_price: Decimal):
        parsed_price = parse_bob_price(raw_price)

        expect(parsed_price).to(equal(expected_price))

    @pytest.mark.parametrize("raw_price", [None, "", "consultar", "Bs."])
    def test_returns_none_without_digits(self, raw_price: str | None):
        parsed_price = parse_bob_price(raw_price)

        expect(parsed_price).to(be_none)
