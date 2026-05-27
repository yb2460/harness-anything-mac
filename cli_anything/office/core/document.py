"""WPS CLI - 文档管理（创建/打开/保存/信息）。"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

PROJECT_VERSION = "1.0"
VALID_DOC_TYPES = ("writer", "calc", "impress")

PAGE_PROFILES = {
    "a4_portrait": {
        "name": "A4 纵向",
        "page_width": "21cm", "page_height": "29.7cm",
        "margin_top": "2.54cm", "margin_bottom": "2.54cm",
        "margin_left": "3.18cm", "margin_right": "3.18cm",
    },
    "a4_landscape": {
        "name": "A4 横向",
        "page_width": "29.7cm", "page_height": "21cm",
        "margin_top": "2.54cm", "margin_bottom": "2.54cm",
        "margin_left": "2.54cm", "margin_right": "2.54cm",
    },
    "letter_portrait": {
        "name": "Letter 纵向",
        "page_width": "21.59cm", "page_height": "27.94cm",
        "margin_top": "2.54cm", "margin_bottom": "2.54cm",
        "margin_left": "2.54cm", "margin_right": "2.54cm",
    },
    "presentation_16_9": {
        "name": "宽屏 16:9",
        "page_width": "25.4cm", "page_height": "14.29cm",
    },
    "presentation_4_3": {
        "name": "标准 4:3",
        "page_width": "25.4cm", "page_height": "19.05cm",
    },
}


def create_document(
    doc_type: str = "writer",
    name: str = "untitled",
    profile: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """创建一个新的文档项目。

    Args:
        doc_type: 文档类型 —— writer / calc / impress
        name: 文档名称
        profile: 页面配置文件名称
        settings: 自定义页面设置（覆盖配置文件默认值）

    Returns:
        包含完整文档结构的新项目字典
    """
    if doc_type not in VALID_DOC_TYPES:
        raise ValueError(f"不支持的文档类型: {doc_type}。有效值: {VALID_DOC_TYPES}")

    now = datetime.now().isoformat()

    project = {
        "version": PROJECT_VERSION,
        "name": name,
        "type": doc_type,
        "settings": {},
        "styles": {},
        "metadata": {
            "title": name,
            "author": "",
            "description": "",
            "subject": "",
            "created": now,
            "modified": now,
            "software": "cli-anything-wps 1.0.0",
        },
    }

    # 应用页面配置文件
    if profile and profile in PAGE_PROFILES:
        project["settings"] = dict(PAGE_PROFILES[profile])
    elif profile:
        available = ", ".join(PAGE_PROFILES.keys())
        raise ValueError(f"不支持的页面配置: {profile}。可用: {available}")

    # 覆盖自定义设置
    if settings:
        project["settings"].update(settings)

    # 按文档类型添加特定结构
    if doc_type == "writer":
        project["content"] = []
    elif doc_type == "calc":
        project["sheets"] = [{"name": "Sheet1", "cells": {}}]
    elif doc_type == "impress":
        project["slides"] = []

    return project


def open_document(path: str) -> Dict[str, Any]:
    """打开现有的 WPS CLI 项目文件。

    Args:
        path: .wps-cli.json 文件路径

    Returns:
        项目字典
    """
    if not path.endswith(".json"):
        raise ValueError(f"仅支持 .json 文件。对于 Office 文件，请导入后打开。")

    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "version" not in data or "type" not in data:
        raise ValueError(f"不是有效的 WPS CLI 项目文件: {path}")

    if data.get("type") not in VALID_DOC_TYPES:
        raise ValueError(f"未知的文档类型: {data.get('type')}")

    return data


def save_document(project: Dict[str, Any], path: str) -> str:
    """保存文档项目到 JSON 文件。

    Args:
        project: 项目字典
        path: 保存路径（.json）

    Returns:
        保存的绝对路径
    """
    project["metadata"]["modified"] = datetime.now().isoformat()
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2, ensure_ascii=False, default=str)

    return abs_path


def get_document_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """获取文档信息摘要。

    Args:
        project: 项目字典

    Returns:
        包含文档元数据和统计信息的字典
    """
    info = {
        "name": project.get("name", "unnamed"),
        "version": project.get("version", "unknown"),
        "type": project.get("type", "unknown"),
        "settings": project.get("settings", {}),
        "metadata": project.get("metadata", {}),
        "styles_count": len(project.get("styles", {})),
    }

    doc_type = project.get("type", "writer")
    if doc_type == "writer":
        info["content_count"] = len(project.get("content", []))
    elif doc_type == "calc":
        info["sheet_count"] = len(project.get("sheets", []))
        info["sheets"] = []
        for sheet in project.get("sheets", []):
            info["sheets"].append({
                "name": sheet.get("name", "unknown"),
                "cell_count": len(sheet.get("cells", {})),
            })
    elif doc_type == "impress":
        info["slide_count"] = len(project.get("slides", []))

    return info


def list_profiles() -> List[Dict[str, Any]]:
    """列出所有可用的页面配置文件。"""
    return [
        {"id": key, **value}
        for key, value in PAGE_PROFILES.items()
    ]
