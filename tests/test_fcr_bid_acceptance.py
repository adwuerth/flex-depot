"""FCR price-based bid acceptance and capacity-price forecast error settings."""

import math

import pytest
from pydantic import ValidationError

from flex_dep_opt.config.settings import FCRForecastErrorSettings, FCRSettings
from flex_dep_opt.workflows.mpc_workflow import _fcr_bid_decision


def test_bid_at_breakeven_is_accepted_when_price_reaches_it():
    assert _fcr_bid_decision(5.0, 0.0, 5.0) == (5.0, True)
    assert _fcr_bid_decision(5.0, 0.0, 24.0) == (5.0, True)
    assert _fcr_bid_decision(5.0, 0.0, 4.99) == (5.0, False)


def test_markup_raises_the_bid_price():
    assert _fcr_bid_decision(5.0, 10.0, 14.0) == (15.0, False)
    assert _fcr_bid_decision(5.0, 10.0, 15.0) == (15.0, True)


def test_missing_or_negative_breakeven_bids_as_price_taker():
    assert _fcr_bid_decision(math.nan, 0.0, 0.0) == (0.0, True)
    assert _fcr_bid_decision(-3.0, 2.0, 1.0) == (2.0, False)


def test_settings_default_is_disabled():
    fcr = FCRSettings(prices_source="x.xlsx")
    assert fcr.bid_acceptance is False
    assert fcr.bid_markup_eur_per_mw == 0.0
    assert fcr.forecast_error.enabled is False


def test_settings_reject_invalid_values():
    with pytest.raises(ValidationError):
        FCRSettings(prices_source="x.xlsx", bid_markup_eur_per_mw=-1.0)
    with pytest.raises(ValidationError):
        FCRForecastErrorSettings(sigma_eur_per_mw=-1.0)
    with pytest.raises(ValidationError):
        FCRForecastErrorSettings(rho=1.0)
