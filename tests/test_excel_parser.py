from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from excel_parser import (
    convert_unit_if_needed,
    find_sheets_by_type,
    load_workbook_data,
    normalize_sheet_name,
    parse_to_storage_input,
)


@dataclass
class FakeCell:
    row: int
    column: int
    value: Any

    @property
    def coordinate(self) -> str:
        return f"{chr(64 + self.column)}{self.row}"


class FakeSheet:
    def __init__(self, title: str, rows: list[list[Any]]) -> None:
        self.title = title
        self._rows = rows

    def iter_rows(self) -> list[list[FakeCell]]:
        return [
            [FakeCell(row_index, column_index, value) for column_index, value in enumerate(row, start=1)]
            for row_index, row in enumerate(self._rows, start=1)
        ]

    def cell(self, row: int, column: int) -> FakeCell:
        try:
            value = self._rows[row - 1][column - 1]
        except IndexError:
            value = None
        return FakeCell(row, column, value)


class FakeWorkbook:
    def __init__(self, worksheets: list[FakeSheet]) -> None:
        self.worksheets = worksheets


def test_load_workbook_data_returns_non_empty_cells(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("Summary", [["contract_capacity_kw", 600], [None, "   "]]),
            FakeSheet("Reserve", [["sr_price", 250]]),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    result = load_workbook_data("ignored.xlsx")

    assert result == [
        ("Summary", "A1", 1, 1, "contract_capacity_kw"),
        ("Summary", "B1", 1, 2, 600),
        ("Reserve", "A1", 1, 1, "sr_price"),
        ("Reserve", "B1", 1, 2, 250),
    ]


def test_normalize_sheet_name_trims_spaces() -> None:
    assert normalize_sheet_name("  年度收益  ") == "年度收益"


def test_sheet_token_matching_detects_required_types() -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("鼎宸-24小時策略試算(商一)", [["x"]]),
            FakeSheet("派能-24小時策略試算(商二)", [["x"]]),
            FakeSheet("年度收益 ", [["x"]]),
        ]
    )

    classified = find_sheets_by_type(workbook)

    assert [sheet.title for sheet in classified["strategy"]] == [
        "鼎宸-24小時策略試算(商一)",
        "派能-24小時策略試算(商二)",
    ]
    assert [sheet.title for sheet in classified["annual_result"]] == ["年度收益 "]


def test_convert_power_mw_to_kw() -> None:
    assert convert_unit_if_needed("power_kw", 1.5, "MW") == 1500


def test_convert_capacity_mwh_to_kwh() -> None:
    assert convert_unit_if_needed("capacity_kwh", 2.2, "MWh") == 2200


def test_convert_discount_percent_to_ratio() -> None:
    assert convert_unit_if_needed("dr_discount_ratio", 120, None) == 1.2


def test_convert_discount_percent_text_to_ratio() -> None:
    assert convert_unit_if_needed("dr_discount_ratio", 120, "120%") == 1.2


def test_efficiency_prefers_efficiency_not_loss(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("案場資訊", [["效率損失", "8%"], ["轉換效率", "92%"]]),
            FakeSheet("24小時 排程", [["x"]]),
            FakeSheet("派能-24小時策略試算(商二)", [["平日尖峰-離峰", 3.1, 2.4]]),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, _ = parse_to_storage_input("ignored.xlsx")

    assert parsed.efficiency == 0.92


def test_sr_price_avoids_first_non_price_numeric(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("案場資訊", [["契約容量", 600], ["充放電功率", 500], ["總額定儲能容量", 1000], ["充放電深度", 90], ["效率", 92]]),
            FakeSheet("24小時 排程", [["x"]]),
            FakeSheet(
                "派能-24小時策略試算(商二)",
                [
                    ["平日尖峰-離峰", 3.1, 2.4],
                    ["首年容量費", 100, "NTD/kW-月"],
                ],
            ),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, _ = parse_to_storage_input("ignored.xlsx")
    assert parsed.sr_price == 100


def test_dr_hours_with_only_options_keeps_default(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("案場資訊", [["契約容量", 600], ["充放電功率", 500], ["總額定儲能容量", 1000], ["充放電深度", 90], ["效率", 92]]),
            FakeSheet("24小時 排程", [["連續2小時", 2], ["連續4小時", 4], ["連續6小時", 6]]),
            FakeSheet("派能-24小時策略試算(商二)", [["平日尖峰-離峰", 3.1, 2.4]]),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, warnings = parse_to_storage_input("ignored.xlsx")

    assert parsed.dr_hours == 2.0
    assert any("dr_hours" in warning for warning in warnings)


def test_parse_rejects_out_of_range_value_and_warns(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet("案場資訊", [["契約容量", 600], ["充放電功率", 500], ["總額定儲能容量", 1000], ["充放電深度", 90], ["效率", 92]]),
            FakeSheet("24小時 排程", [["需量反應執行率", 6]]),
            FakeSheet(
                "派能-24小時策略試算(商二)",
                [["平日尖峰-離峰", 3.1, 2.4], ["即時備轉容量", 300]],
            ),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, warnings = parse_to_storage_input("ignored.xlsx")

    assert parsed.dr_execution_rate == 1.0
    assert any("dr_execution_rate" in warning and "超出合理範圍" in warning for warning in warnings)
