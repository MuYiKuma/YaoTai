import pytest

from calculator import (
    calculate_arbitrage_revenue_breakdown,
    calculate_available_energy,
    calculate_sr_revenue_breakdown,
    calculate_total_revenue_breakdown,
)
from storage_site_input import StorageSiteInput


def test_calculate_available_energy() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        round_trip_efficiency=0.92,
    )

    result = calculate_available_energy(input_data)

    assert result == 828.0


def test_calculate_arbitrage_revenue_breakdown_seasonal_days() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        round_trip_efficiency=0.92,
        summer_spread_per_kwh=2.5,
        non_summer_spread_per_kwh=2.0,
        summer_cycles_per_day=1.5,
        non_summer_cycles_per_day=1.2,
        summer_days_per_year=120,
        non_summer_days_per_year=245,
    )

    result = calculate_arbitrage_revenue_breakdown(input_data)

    assert result["summer_revenue"] == 372600.0
    assert result["non_summer_revenue"] == pytest.approx(486864.0)
    assert result["total_revenue"] == 859464.0


def test_calculate_sr_revenue_breakdown_annual_revenue() -> None:
    input_data = StorageSiteInput(
        sr_enabled=True,
        sr_bid_capacity_kw=1000,
        sr_standby_hours_per_day=2,
        sr_capacity_fee_per_mwh=400,
        sr_performance_fee_per_mwh=100,
        sr_adjustment_factor=0.8,
        sr_days_per_year=300,
        sr_service_fee_ratio=0.1,
    )

    result = calculate_sr_revenue_breakdown(input_data)

    assert result["daily_gross_revenue"] == 800.0
    assert result["annual_gross_revenue"] == 240000.0
    assert result["service_fee"] == 24000.0
    assert result["total_revenue"] == 216000.0


def test_calculate_total_revenue_breakdown_aggregation() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=500,
        dod=1.0,
        soh=1.0,
        round_trip_efficiency=1.0,
        summer_spread_per_kwh=2.0,
        non_summer_spread_per_kwh=1.0,
        summer_cycles_per_day=1.0,
        non_summer_cycles_per_day=1.0,
        summer_days_per_year=100,
        non_summer_days_per_year=200,
        dr_enabled=True,
        dr_committed_capacity_kw=100,
        dr_event_hours=2,
        dr_events_per_year=10,
        dr_price_per_kw_event=20,
        dr_discount_ratio=0.1,
        sr_enabled=True,
        sr_bid_capacity_kw=100,
        sr_standby_hours_per_day=1,
        sr_capacity_fee_per_mwh=500,
        sr_performance_fee_per_mwh=500,
        sr_adjustment_factor=1.0,
        sr_days_per_year=100,
        sr_service_fee_ratio=0.2,
    )

    result = calculate_total_revenue_breakdown(input_data)

    assert result["arbitrage"]["total_revenue"] == 200000.0
    assert result["dr"]["total_revenue"] == 18000.0
    assert result["sr"]["total_revenue"] == 8000.0
    assert result["total_revenue"] == 226000.0


def test_calculate_sr_revenue_breakdown_disabled_returns_zero() -> None:
    input_data = StorageSiteInput(
        sr_enabled=False,
        sr_bid_capacity_kw=1000,
        sr_standby_hours_per_day=2,
        sr_capacity_fee_per_mwh=400,
        sr_performance_fee_per_mwh=100,
        sr_adjustment_factor=0.8,
        sr_days_per_year=300,
        sr_service_fee_ratio=0.1,
    )

    result = calculate_sr_revenue_breakdown(input_data)

    assert result["bid_capacity_kw"] == 0.0
    assert result["daily_gross_revenue"] == 0.0
    assert result["annual_gross_revenue"] == 0.0
    assert result["service_fee"] == 0.0
    assert result["total_revenue"] == 0.0


def test_calculate_arbitrage_revenue_breakdown_sensitive_to_efficiency() -> None:
    high_efficiency_input = StorageSiteInput(
        capacity_kwh=1000,
        dod=1.0,
        soh=1.0,
        round_trip_efficiency=1.0,
        summer_spread_per_kwh=2.0,
        non_summer_spread_per_kwh=2.0,
        summer_cycles_per_day=1.0,
        non_summer_cycles_per_day=1.0,
        summer_days_per_year=100,
        non_summer_days_per_year=100,
    )

    low_efficiency_input = StorageSiteInput(
        capacity_kwh=1000,
        dod=1.0,
        soh=1.0,
        round_trip_efficiency=0.5,
        summer_spread_per_kwh=2.0,
        non_summer_spread_per_kwh=2.0,
        summer_cycles_per_day=1.0,
        non_summer_cycles_per_day=1.0,
        summer_days_per_year=100,
        non_summer_days_per_year=100,
    )

    high_result = calculate_arbitrage_revenue_breakdown(high_efficiency_input)
    low_result = calculate_arbitrage_revenue_breakdown(low_efficiency_input)

    assert high_result["available_energy_kwh"] == 1000.0
    assert low_result["available_energy_kwh"] == 500.0
    assert low_result["total_revenue"] < high_result["total_revenue"]
    assert low_result["total_revenue"] == 200000.0
    assert high_result["total_revenue"] == 400000.0
