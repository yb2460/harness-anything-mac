"""WPS CLI - Writer（文字处理）命令实现。"""

from typing import Dict, Any, Optional, List


def _ensure_writer(project: Dict[str, Any]) -> None:
    """确保项目是 Writer 类型。"""
    if project.get("type") != "writer":
        raise ValueError("当前文档不是 Writer（文字）类型。")


def _get_content_list(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """获取内容列表，如不存在则创建。"""
    _ensure_writer(project)
    if "content" not in project:
        project["content"] = []
    return project["content"]


def add_paragraph(
    project: Dict[str, Any],
    text: str = "",
    style: Optional[Dict[str, Any]] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加段落。

    Args:
        project: 项目字典
        text: 段落文本
        style: 样式字典（字体大小、粗体、斜体等）
        position: 插入位置（None = 末尾）

    Returns:
        创建的段落内容项
    """
    content = _get_content_list(project)
    item = {
        "type": "paragraph",
        "text": text,
        "style": style or {},
    }
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def add_heading(
    project: Dict[str, Any],
    text: str = "",
    level: int = 1,
    style: Optional[Dict[str, Any]] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加标题。

    Args:
        project: 项目字典
        text: 标题文本
        level: 标题级别（1-6）
        style: 样式字典
        position: 插入位置

    Returns:
        创建的标题内容项
    """
    if not (1 <= level <= 6):
        raise ValueError(f"标题级别需在 1-6 之间，当前值: {level}")

    content = _get_content_list(project)
    item = {
        "type": "heading",
        "level": level,
        "text": text,
        "style": style or {},
    }
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def add_list(
    project: Dict[str, Any],
    items: Optional[List[str]] = None,
    list_style: str = "bullet",
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加列表。

    Args:
        project: 项目字典
        items: 列表内容
        list_style: bullet（无序）或 number（有序）
        position: 插入位置

    Returns:
        创建的列表内容项
    """
    if list_style not in ("bullet", "number"):
        raise ValueError(f"列表样式需为 bullet 或 number，当前值: {list_style}")

    content = _get_content_list(project)
    item = {
        "type": "list",
        "list_style": list_style,
        "items": list(items) if items else [],
    }
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def add_table(
    project: Dict[str, Any],
    rows: int = 2,
    cols: int = 2,
    data: Optional[List[List[str]]] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加表格。

    Args:
        project: 项目字典
        rows: 行数
        cols: 列数
        data: 表格数据（未提供时生成空单元格）
        position: 插入位置

    Returns:
        创建的表格内容项
    """
    if rows < 1 or cols < 1:
        raise ValueError(f"表格行和列必须 >= 1，当前值: rows={rows}, cols={cols}")

    content = _get_content_list(project)
    if data is None:
        data = [[""] * cols for _ in range(rows)]

    item = {
        "type": "table",
        "rows": rows,
        "cols": cols,
        "data": data,
    }
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def add_page_break(
    project: Dict[str, Any],
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加分页符。"""
    content = _get_content_list(project)
    item = {"type": "page_break"}
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def add_image(
    project: Dict[str, Any],
    image_path: str,
    width: str = "10cm",
    height: str = "10cm",
    name: Optional[str] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """添加图片引用。

    Args:
        project: 项目字典
        image_path: 图片文件路径
        width: 显示宽度
        height: 显示高度
        name: 图片名称
        position: 插入位置
    """
    content = _get_content_list(project)
    item = {
        "type": "image_ref",
        "name": name or os.path.basename(image_path),
        "path": image_path,
        "width": width,
        "height": height,
    }
    if position is not None and 0 <= position < len(content):
        content.insert(position, item)
    else:
        content.append(item)
    return item


def remove_content(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """按索引删除内容项。"""
    content = _get_content_list(project)
    if index < 0 or index >= len(content):
        raise IndexError(f"索引超出范围: {index}（共 {len(content)} 项）")
    removed = content.pop(index)
    return removed


def list_content(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """列出所有内容项（含预览）。"""
    content = _get_content_list(project)
    result = []
    for i, item in enumerate(content):
        item_type = item.get("type", "unknown")
        preview = ""
        if item_type == "paragraph":
            preview = item.get("text", "")[:80]
        elif item_type == "heading":
            preview = f"H{item.get('level', 1)}: {item.get('text', '')[:60]}"
        elif item_type == "list":
            preview = f"{item.get('list_style', 'bullet')}: {len(item.get('items', []))} 项"
        elif item_type == "table":
            preview = f"{item.get('rows', 0)}x{item.get('cols', 0)} 表格"
        elif item_type == "page_break":
            preview = "--- 分页符 ---"
        elif item_type == "image_ref":
            preview = f"图片: {item.get('name', 'unknown')}"
        result.append({
            "index": i,
            "type": item_type,
            "preview": preview,
        })
    return result


def get_content(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """按索引获取内容项详情。"""
    content = _get_content_list(project)
    if index < 0 or index >= len(content):
        raise IndexError(f"索引超出范围: {index}（共 {len(content)} 项）")
    return content[index]


def set_content_text(
    project: Dict[str, Any],
    index: int,
    text: str,
) -> Dict[str, Any]:
    """设置内容项的文本（仅适用于段落和标题）。"""
    content = _get_content_list(project)
    if index < 0 or index >= len(content):
        raise IndexError(f"索引超出范围: {index}（共 {len(content)} 项）")
    item = content[index]
    if item.get("type") not in ("paragraph", "heading"):
        raise ValueError(f"仅段落和标题支持设置文本，当前类型: {item.get('type')}")
    item["text"] = text
    return item


def find_replace(
    project: Dict[str, Any],
    find_text: str,
    replace_text: str,
) -> Dict[str, Any]:
    """查找并替换文档中的文本。

    Args:
        project: 项目字典
        find_text: 要查找的文本
        replace_text: 替换为的文本

    Returns:
        包含替换计数和替换详情的结果字典
    """
    content = _get_content_list(project)
    replaced = 0
    details = []

    for i, item in enumerate(content):
        if item.get("type") in ("paragraph", "heading"):
            old = item.get("text", "")
            if find_text in old:
                item["text"] = old.replace(find_text, replace_text)
                replaced += 1
                details.append({"index": i, "type": item["type"], "before": old[:80]})

        elif item.get("type") == "list":
            for j, li in enumerate(item.get("items", [])):
                if find_text in li:
                    item["items"][j] = li.replace(find_text, replace_text)
                    replaced += 1
                    details.append({"index": i, "type": "list", "item_index": j})

        elif item.get("type") == "table":
            for ri, row in enumerate(item.get("data", [])):
                for ci, cell in enumerate(row):
                    if find_text in str(cell):
                        item["data"][ri][ci] = str(cell).replace(find_text, replace_text)
                        replaced += 1
                        details.append({"index": i, "type": "table", "row": ri, "col": ci})

    return {"replaced": replaced, "details": details}


import os  # noqa: E402（add_image 中使用）
