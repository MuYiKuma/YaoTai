from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from excel_parser import load_workbook_data, parse_to_storage_input


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


def test_parse_to_storage_input_reads_keywords_from_right_or_below(monkeypatch) -> None:
    workbook = FakeWorkbook(
        [
            FakeSheet(
                "Summary",
                [
                    ["contract_capacity_kw", 600],
                    ["power_kw", None],
                    [550, "capacity_kwh", 1200],
                    ["dod", 0.85],
                    ["efficiency", 0.93],
                    ["summer_spread", 3.1],
                    ["non_summer_spread", 2.4],
                    ["summer_cycles_per_day", 1.8],
                    ["non_summer_cycles_per_day", 1.1],
                    ["dr_capacity_kw", 50],
                    ["dr_hours", 3],
                    ["dr_rate", 100],
                    ["dr_execution_rate", 0.7],
                    ["dr_discount_ratio", 0.8],
                ],
            ),
            FakeSheet(
                "Reserve",
                [
                    ["sr_capacity_kw", 80],
                    ["sr_price", 250],
                    ["sr_hours_per_day", 4],
                    ["sr_execution_rate", 0.9],
                ],
            ),
        ]
    )
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, warnings = parse_to_storage_input("ignored.xlsx")

    assert parsed.contract_capacity_kw == 600
    assert parsed.power_kw == 550
    assert parsed.capacity_kwh == 1200
    assert parsed.dod == 0.85
    assert parsed.efficiency == 0.93
    assert parsed.summer_spread == 3.1
    assert parsed.non_summer_spread == 2.4
    assert parsed.summer_cycles_per_day == 1.8
    assert parsed.non_summer_cycles_per_day == 1.1
    assert parsed.dr_capacity_kw == 50
    assert parsed.dr_hours == 3
    assert parsed.dr_rate == 100
    assert parsed.dr_execution_rate == 0.7
    assert parsed.dr_discount_ratio == 0.8
    assert parsed.sr_capacity_kw == 80
    assert parsed.sr_price == 250
    assert parsed.sr_hours_per_day == 4
    assert parsed.sr_execution_rate == 0.9
    assert warnings == []


def test_parse_to_storage_input_adds_warning_when_field_missing(monkeypatch) -> None:
    workbook = FakeWorkbook([FakeSheet("Input", [["contract_capacity_kw", 700]])])
    monkeypatch.setattr("excel_parser._load_workbook", lambda _: workbook)

    parsed, warnings = parse_to_storage_input("ignored.xlsx")

    assert parsed.contract_capacity_kw == 700
    assert parsed.power_kw == 500
    assert "找不到欄位 power_kw 的值，已保留預設值 500.0。" in warnings
    assert "找不到欄位 sr_execution_rate 的值，已保留預設值 1.0。" in warnings
