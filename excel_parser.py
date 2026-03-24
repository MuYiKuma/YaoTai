from __future__ import annotations

from dataclasses import fields
import re
from typing import Any

from storage_site_input import StorageSiteInput

WorkbookCell = tuple[str, str, int, int, Any]

_FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "contract_capacity_kw": ("contract_capacity_kw", "contract capacity", "契約容量"),
    "power_kw": ("power_kw", "power", "功率"),
    "capacity_kwh": ("capacity_kwh", "capacity kwh", "容量", "電量"),
    "dod": ("dod", "depth of discharge"),
    "efficiency": ("efficiency", "效率"),
    "summer_spread": ("summer_spread", "summer spread", "夏月價差"),
    "non_summer_spread": (
        "non_summer_spread",
        "non summer spread",
        "non-summer spread",
        "非夏月價差",
    ),
    "summer_cycles_per_day": (
        "summer_cycles_per_day",
        "summer cycles per day",
        "夏月循環",
    ),
    "non_summer_cycles_per_day": (
        "non_summer_cycles_per_day",
        "non summer cycles per day",
        "non-summer cycles per day",
        "非夏月循環",
    ),
    "dr_capacity_kw": ("dr_capacity_kw", "dr capacity", "需量反應容量"),
    "dr_hours": ("dr_hours", "dr hours", "需量反應時數"),
    "dr_rate": ("dr_rate", "dr rate", "需量反應費率"),
    "dr_execution_rate": (
        "dr_execution_rate",
        "dr execution rate",
        "需量反應執行率",
    ),
    "dr_discount_ratio": (
        "dr_discount_ratio",
        "dr discount ratio",
        "需量反應折扣比例",
    ),
    "sr_capacity_kw": ("sr_capacity_kw", "sr capacity", "即時備轉容量"),
    "sr_price": ("sr_price", "sr price", "即時備轉價格"),
    "sr_hours_per_day": (
        "sr_hours_per_day",
        "sr hours per day",
        "即時備轉每日時數",
    ),
    "sr_execution_rate": (
        "sr_execution_rate",
        "sr execution rate",
        "即時備轉執行率",
    ),
}

_NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:\.\d+)?")


def _load_workbook(file_path: str) -> Any:
    from openpyxl import load_workbook

    return load_workbook(file_path, data_only=True)


def _normalize_text(value: Any) -> str:
    text = str(value).strip().lower()
    return re.sub(r"[_\-\s]+", " ", text)


def _extract_numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    match = _NUMBER_PATTERN.search(str(value).replace(",", ""))
    if match is None:
        return None
    return float(match.group())


def load_workbook_data(file_path: str) -> list[WorkbookCell]:
    """
    回傳所有工作表中的非空白儲存格資料
    格式為：
    [(sheet_name, cell_coordinate, row, column, value), ...]
    """
    workbook = _load_workbook(file_path)
    results: list[WorkbookCell] = []

    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                if isinstance(cell.value, str) and not cell.value.strip():
                    continue
                results.append(
                    (sheet.title, cell.coordinate, cell.row, cell.column, cell.value)
                )

    return results


def _find_neighbor_numeric_value(sheet: Any, row: int, column: int) -> float | None:
    for row_offset, column_offset in ((0, 1), (1, 0)):
        value = sheet.cell(row=row + row_offset, column=column + column_offset).value
        numeric_value = _extract_numeric(value)
        if numeric_value is not None:
            return numeric_value
    return None


def parse_to_storage_input(file_path: str) -> tuple[StorageSiteInput, list[str]]:
    """
    從 Excel 中抓取關鍵欄位，回傳：
    - StorageSiteInput
    - warnings list
    """
    workbook = _load_workbook(file_path)
    parsed_values: dict[str, float] = {}
    warnings: list[str] = []

    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if not isinstance(cell.value, str) or not cell.value.strip():
                    continue

                normalized_value = _normalize_text(cell.value)
                for field_name, keywords in _FIELD_KEYWORDS.items():
                    if field_name in parsed_values:
                        continue
                    if any(_normalize_text(keyword) in normalized_value for keyword in keywords):
                        numeric_value = _find_neighbor_numeric_value(
                            sheet, cell.row, cell.column
                        )
                        if numeric_value is not None:
                            parsed_values[field_name] = numeric_value
                        break

    init_values: dict[str, float] = {}
    for field in fields(StorageSiteInput):
        if field.name not in _FIELD_KEYWORDS:
            continue
        if field.name in parsed_values:
            init_values[field.name] = parsed_values[field.name]
        else:
            warnings.append(
                f"找不到欄位 {field.name} 的值，已保留預設值 {field.default}。"
            )

    return StorageSiteInput(**init_values), warnings
