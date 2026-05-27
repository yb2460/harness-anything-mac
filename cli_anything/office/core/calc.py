"""WPS CLI - Calc（电子表格）命令实现。"""

from typing import Dict, Any, Optional, List
import re


def _ensure_calc(project: Dict[str, Any]) -> None:
    """确保项目是 Calc 类型。"""
    if project.get("type") != "calc":
        raise ValueError("当前文档不是 Calc（电子表格）类型。")


def _get_sheet(project: Dict[str, Any], sheet: int = 0) -> Dict[str, Any]:
    """按索引获取工作表。"""
    _ensure_calc(project)
    sheets = project.get("sheets", [])
    if sheet < 0 or sheet >= len(sheets):
        raise IndexError(f"工作表索引超出范围: {sheet}（共 {len(sheets)} 个）")
    return sheets[sheet]


def _validate_cell_ref(ref: str) -> str:
    """验证并规范化单元格引用（如 A1, B2, AA10）。"""
    match = re.match(r"^([A-Za-z]{1,3})(\d+)$", ref)
    if not match:
        raise ValueError(f"无效的单元格引用: {ref}。请使用如 A1、B2、AA10 的格式。")
    col = match.group(1).upper()
    row = int(match.group(2))
    return f"{col}{row}"


def add_sheet(
    project: Dict[str, Any],
    name: str = "Sheet",
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加新工作表。"""
    _ensure_calc(project)
    if "sheets" not in project:
        project["sheets"] = []

    sheet = {"name": name, "cells": {}}
    sheets = project["sheets"]
    if position is not None and 0 <= position < len(sheets):
        sheets.insert(position, sheet)
    else:
        sheets.append(sheet)
    return sheet


def remove_sheet(project: Dict[str, Any], sheet: int) -> Dict[str, Any]:
    """按索引删除工作表。"""
    _ensure_calc(project)
    sheets = project.get("sheets", [])
    if sheet < 0 or sheet >= len(sheets):
        raise IndexError(f"工作表索引超出范围: {sheet}（共 {len(sheets)} 个）")
    removed = sheets.pop(sheet)
    return removed


def rename_sheet(project: Dict[str, Any], sheet: int, name: str) -> Dict[str, Any]:
    """重命名工作表。"""
    s = _get_sheet(project, sheet)
    s["name"] = name
    return s


def set_cell(
    project: Dict[str, Any],
    ref: str,
    value: Any,
    cell_type: str = "string",
    sheet: int = 0,
    formula: Optional[str] = None,
) -> Dict[str, Any]:
    """设置单元格的值。

    Args:
        project: 项目字典
        ref: 单元格引用（如 A1）
        value: 单元格值
        cell_type: 数据类型 —— string / float / boolean / formula
        sheet: 工作表索引
        formula: 公式字符串

    Returns:
        设置的单元格信息
    """
    ref = _validate_cell_ref(ref)
    s = _get_sheet(project, sheet)

    # 自动推断数据类型
    if cell_type == "string":
        try:
            float(value)
            cell_type = "float"
        except (ValueError, TypeError):
            pass

    cell = {"value": value, "type": cell_type}
    if formula:
        cell["formula"] = formula

    s["cells"][ref] = cell
    return {"ref": ref, "sheet": sheet, **cell}


def get_cell(
    project: Dict[str, Any],
    ref: str,
    sheet: int = 0,
) -> Dict[str, Any]:
    """获取单元格的值。"""
    ref = _validate_cell_ref(ref)
    s = _get_sheet(project, sheet)
    cell = s["cells"].get(ref)
    if cell is None:
        return {"ref": ref, "sheet": sheet, "value": None, "type": "empty"}
    return {"ref": ref, "sheet": sheet, **cell}


def clear_cell(
    project: Dict[str, Any],
    ref: str,
    sheet: int = 0,
) -> Dict[str, Any]:
    """清除单元格。"""
    ref = _validate_cell_ref(ref)
    s = _get_sheet(project, sheet)
    s["cells"].pop(ref, None)
    return {"ref": ref, "sheet": sheet, "cleared": True}


def set_range(
    project: Dict[str, Any],
    start_ref: str,
    data: List[List[Any]],
    sheet: int = 0,
) -> Dict[str, Any]:
    """批量写入一个矩形区域的数据。

    Args:
        project: 项目字典
        start_ref: 起始单元格引用（如 A1）
        data: 二维数据数组
        sheet: 工作表索引

    Returns:
        包含写入单元格数量的结果字典
    """
    start_ref = _validate_cell_ref(start_ref)
    s = _get_sheet(project, sheet)

    start_col = re.match(r"^([A-Za-z]+)", start_ref).group(1).upper()
    start_row = int(re.match(r"^[A-Za-z]+(\d+)$", start_ref).group(1))

    count = 0
    for ri, row in enumerate(data):
        for ci, value in enumerate(row):
            col = _num_to_col(_col_to_num(start_col) + ci)
            ref = f"{col}{start_row + ri}"
            cell_type = "string"
            try:
                float(value)
                cell_type = "float"
            except (ValueError, TypeError):
                pass
            s["cells"][ref] = {"value": value, "type": cell_type}
            count += 1

    return {"cells_set": count, "start": start_ref, "rows": len(data), "cols": max(len(r) for r in data) if data else 0}


def merge_cells(
    project: Dict[str, Any],
    start_ref: str,
    end_ref: str,
    sheet: int = 0,
) -> Dict[str, Any]:
    """标记合并单元格区域。"""
    start_ref = _validate_cell_ref(start_ref)
    end_ref = _validate_cell_ref(end_ref)
    s = _get_sheet(project, sheet)

    if "merged_cells" not in s:
        s["merged_cells"] = []

    merge_entry = {"start": start_ref, "end": end_ref}
    s["merged_cells"].append(merge_entry)
    return merge_entry


def list_sheets(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """列出所有工作表。"""
    _ensure_calc(project)
    sheets = project.get("sheets", [])
    result = []
    for i, sheet in enumerate(sheets):
        result.append({
            "index": i,
            "name": sheet.get("name", "unknown"),
            "cell_count": len(sheet.get("cells", {})),
        })
    return result


def get_sheet_data(project: Dict[str, Any], sheet: int = 0) -> Dict[str, Any]:
    """获取工作表的完整数据。"""
    return _get_sheet(project, sheet)


# ── 辅助函数 ────────────────────────────────────────────────────

def _col_to_num(col: str) -> int:
    """列字母转数字（A=1, B=2, ..., Z=26, AA=27）。"""
    n = 0
    for c in col.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


def _num_to_col(n: int) -> str:
    """数字转列字母（1=A, 2=B, 26=Z, 27=AA）。"""
    result = ""
    while n > 0:
        n, m = divmod(n - 1, 26)
        result = chr(ord("A") + m) + result
    return result
