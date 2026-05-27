"""WPS CLI - 样式管理。"""

from typing import Dict, Any, Optional, List

VALID_PROPERTIES = {
    "font_size", "font_name", "bold", "italic", "underline",
    "color", "alignment", "line_height", "margin_top", "margin_bottom",
}


def create_style(
    project: Dict[str, Any],
    name: str,
    family: str = "paragraph",
    parent: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """创建新样式。

    Args:
        project: 项目字典
        name: 样式名称
        family: 样式系列 —— paragraph / text
        parent: 父样式名称
        properties: 样式属性

    Returns:
        创建的样式
    """
    if family not in ("paragraph", "text"):
        raise ValueError(f"样式系列需为 paragraph 或 text。当前值: {family}")

    props = properties or {}
    for k in props:
        if k not in VALID_PROPERTIES:
            raise ValueError(f"不支持的样式属性: {k}。有效属性: {sorted(VALID_PROPERTIES)}")

    style = {"family": family, "properties": props}
    if parent:
        style["parent"] = parent

    project.setdefault("styles", {})[name] = style
    return {"name": name, **style}


def modify_style(
    project: Dict[str, Any],
    name: str,
    properties: Optional[Dict[str, Any]] = None,
    family: Optional[str] = None,
    parent: Optional[str] = None,
) -> Dict[str, Any]:
    """修改已有样式。

    Args:
        project: 项目字典
        name: 样式名称
        properties: 要合并的新属性
        family: 新的样式系列
        parent: 新的父样式

    Returns:
        更新后的样式
    """
    styles = project.get("styles", {})
    if name not in styles:
        raise ValueError(f"样式不存在: {name}")

    style = styles[name]
    if properties:
        for k in properties:
            if k not in VALID_PROPERTIES:
                raise ValueError(f"不支持的样式属性: {k}")
        style["properties"].update(properties)
    if family is not None:
        if family not in ("paragraph", "text"):
            raise ValueError(f"样式系列需为 paragraph 或 text。当前值: {family}")
        style["family"] = family
    if parent is not None:
        style["parent"] = parent

    return {"name": name, **style}


def remove_style(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    """删除样式。"""
    styles = project.get("styles", {})
    if name not in styles:
        raise ValueError(f"样式不存在: {name}")
    removed = styles.pop(name)
    return {"name": name, "removed": True, "was": removed}


def list_styles(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """列出所有样式。"""
    styles = project.get("styles", {})
    return [
        {
            "name": name,
            "family": info.get("family", "paragraph"),
            "parent": info.get("parent", ""),
            "properties": info.get("properties", {}),
        }
        for name, info in styles.items()
    ]


def get_style(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    """获取样式详情。"""
    styles = project.get("styles", {})
    if name not in styles:
        raise ValueError(f"样式不存在: {name}")
    return {"name": name, **styles[name]}


def apply_style(
    project: Dict[str, Any],
    style_name: str,
    content_index: int,
) -> Dict[str, Any]:
    """将样式应用于 Writer 内容项。"""
    if project.get("type") != "writer":
        raise ValueError("样式应用仅支持 Writer（文字处理）文档。")

    styles = project.get("styles", {})
    if style_name not in styles:
        raise ValueError(f"样式不存在: {style_name}")

    content = project.get("content", [])
    if content_index < 0 or content_index >= len(content):
        raise IndexError(f"内容索引超出范围: {content_index}（共 {len(content)} 项）")

    style = styles[style_name]
    content[content_index]["style"] = dict(style.get("properties", {}))
    return {"applied": style_name, "to_index": content_index}
