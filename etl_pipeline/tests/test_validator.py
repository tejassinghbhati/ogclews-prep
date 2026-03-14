from exchange.validator import validate_exchange_data
import pytest

def test_valid_data():
    data = {
        "investment_shock": {2025: 150.5, 2026: 155.8},
        "re_capacity": {2025: 0.0105, 2026: 0.0108}
    }
    validated = validate_exchange_data(data)
    assert validated.investment_shock[2025] == 150.5

def test_invalid_data():
    data = {"investment_shock": "not a dict"}
    with pytest.raises(Exception):
        validate_exchange_data(data)
