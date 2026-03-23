from calculator import (
    calculate_arbitrage_revenue,
    calculate_available_energy,
    detect_arbitrage_risk,
)
from storage_site_input import StorageSiteInput


def test_calculate_available_energy() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        efficiency=0.92,
    )

    result = calculate_available_energy(input_data)

    assert result == 828.0


def test_calculate_arbitrage_revenue() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        efficiency=0.92,
        summer_spread=2.5,
        non_summer_spread=2.0,
        summer_cycles_per_day=1.5,
        non_summer_cycles_per_day=1.2,
    )

    result = calculate_arbitrage_revenue(input_data)

    assert result == 567722.7954


def test_detect_arbitrage_risk_returns_low_risk_with_explanation() -> None:
    input_data = StorageSiteInput()

    result = detect_arbitrage_risk(input_data)

    assert result == {
        "risk_level": "low",
        "reasons": [
            "目前套利假設落在合理區間內，夏月收益占比與循環、效率假設皆未見明顯風險。"
        ],
    }


def test_detect_arbitrage_risk_returns_high_risk_for_multiple_conditions() -> None:
    input_data = StorageSiteInput(
        efficiency=0.85,
        summer_spread=2.0,
        non_summer_spread=3.2,
        summer_cycles_per_day=1.0,
        non_summer_cycles_per_day=1.6,
    )

    result = detect_arbitrage_risk(input_data)

    assert result["risk_level"] == "high"
    assert result["reasons"] == [
        "非夏月套利收入高於夏月套利收入，代表收益結構偏向較不穩定的非夏月情境。",
        "非夏月每日循環次數高於 1.5 次，表示模型假設使用頻率偏高，執行風險較大。",
        "價差假設大於 3 元/度，對市場價差的依賴較高，需留意中度風險。",
        "效率參數未落在合理區間（0.9 至 1），代表效率假設可能未妥善考慮，屬高風險。",
    ]


def test_detect_arbitrage_risk_returns_medium_risk_for_large_spread_only() -> None:
    input_data = StorageSiteInput(
        summer_spread=3.2,
        non_summer_spread=2.0,
        summer_cycles_per_day=1.5,
        non_summer_cycles_per_day=1.0,
        efficiency=0.92,
    )

    result = detect_arbitrage_risk(input_data)

    assert result == {
        "risk_level": "medium",
        "reasons": [
            "價差假設大於 3 元/度，對市場價差的依賴較高，需留意中度風險。"
        ],
    }
