"""WPS CLI - 核心模块单元测试。

测试文档创建、编辑、样式等 Data 层操作（不依赖 WPS COM）。
"""

import pytest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cli_anything.wps.core import document
from cli_anything.wps.core import writer
from cli_anything.wps.core import calc
from cli_anything.wps.core import impress
from cli_anything.wps.core import styles
from cli_anything.wps.core.session import Session


class TestDocumentCreate:
    """测试文档创建。"""

    def test_create_writer(self):
        proj = document.create_document(doc_type="writer", name="test")
        assert proj["type"] == "writer"
        assert proj["name"] == "test"
        assert proj["version"] == "1.0"
        assert "content" in proj
        assert isinstance(proj["content"], list)

    def test_create_calc(self):
        proj = document.create_document(doc_type="calc", name="data")
        assert proj["type"] == "calc"
        assert len(proj["sheets"]) == 1
        assert proj["sheets"][0]["name"] == "Sheet1"

    def test_create_impress(self):
        proj = document.create_document(doc_type="impress", name="slides")
        assert proj["type"] == "impress"
        assert isinstance(proj["slides"], list)
        assert len(proj["slides"]) == 0

    def test_create_with_profile(self):
        proj = document.create_document(
            doc_type="writer", name="a4", profile="a4_portrait",
        )
        assert proj["settings"]["page_width"] == "21cm"
        assert proj["settings"]["page_height"] == "29.7cm"

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            document.create_document(doc_type="invalid")

    def test_invalid_profile(self):
        with pytest.raises(ValueError):
            document.create_document(doc_type="writer", profile="nonexistent")


class TestDocumentIO:
    """测试文档保存和加载。"""

    def test_save_and_open(self, tmp_path):
        proj = document.create_document(doc_type="writer", name="save_test")
        path = os.path.join(tmp_path, "test.wps-cli.json")
        saved = document.save_document(proj, path)
        assert os.path.exists(saved)

        loaded = document.open_document(saved)
        assert loaded["name"] == "save_test"
        assert loaded["type"] == "writer"

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            document.open_document("nonexistent.json")


class TestWriterContent:
    """测试 Writer 内容编辑。"""

    def setup_method(self):
        self.proj = document.create_document(doc_type="writer", name="test")

    def test_add_paragraph(self):
        item = writer.add_paragraph(self.proj, text="Hello")
        assert item["type"] == "paragraph"
        assert item["text"] == "Hello"
        assert len(self.proj["content"]) == 1

    def test_add_heading(self):
        item = writer.add_heading(self.proj, text="Title", level=2)
        assert item["type"] == "heading"
        assert item["level"] == 2
        assert item["text"] == "Title"

    def test_add_heading_invalid_level(self):
        with pytest.raises(ValueError):
            writer.add_heading(self.proj, text="Bad", level=7)

    def test_add_list(self):
        item = writer.add_list(self.proj, items=["a", "b"], list_style="bullet")
        assert item["type"] == "list"
        assert item["items"] == ["a", "b"]

    def test_add_numbered_list(self):
        item = writer.add_list(self.proj, items=["1", "2"], list_style="number")
        assert item["list_style"] == "number"

    def test_add_table(self):
        item = writer.add_table(self.proj, rows=3, cols=2)
        assert item["type"] == "table"
        assert item["rows"] == 3
        assert item["cols"] == 2

    def test_add_page_break(self):
        item = writer.add_page_break(self.proj)
        assert item["type"] == "page_break"

    def test_insert_position(self):
        writer.add_paragraph(self.proj, text="first")
        writer.add_paragraph(self.proj, text="second")
        writer.add_paragraph(self.proj, text="inserted", position=1)
        assert self.proj["content"][1]["text"] == "inserted"
        assert len(self.proj["content"]) == 3

    def test_remove_content(self):
        writer.add_paragraph(self.proj, text="first")
        writer.add_heading(self.proj, text="second", level=1)
        removed = writer.remove_content(self.proj, 0)
        assert removed["text"] == "first"
        assert len(self.proj["content"]) == 1

    def test_remove_out_of_range(self):
        with pytest.raises(IndexError):
            writer.remove_content(self.proj, 0)

    def test_list_content(self):
        writer.add_paragraph(self.proj, text="p1")
        writer.add_heading(self.proj, text="h1", level=1)
        items = writer.list_content(self.proj)
        assert len(items) == 2
        assert items[0]["type"] == "paragraph"
        assert items[1]["type"] == "heading"

    def test_set_text(self):
        writer.add_paragraph(self.proj, text="old")
        writer.set_content_text(self.proj, 0, "new")
        assert self.proj["content"][0]["text"] == "new"

    def test_find_replace(self):
        writer.add_paragraph(self.proj, text="Hello World")
        writer.add_paragraph(self.proj, text="Hello again")
        result = writer.find_replace(self.proj, "Hello", "Hi")
        assert result["replaced"] == 2

    def test_find_replace_in_list(self):
        writer.add_list(self.proj, items=["apple pie", "banana"], list_style="bullet")
        result = writer.find_replace(self.proj, "apple", "orange")
        assert result["replaced"] == 1

    def test_type_check(self):
        proj = document.create_document(doc_type="calc")
        with pytest.raises(ValueError):
            writer.add_paragraph(proj, text="bad")


class TestCalcContent:
    """测试 Calc 电子表格编辑。"""

    def setup_method(self):
        self.proj = document.create_document(doc_type="calc", name="test")

    def test_add_sheet(self):
        sheet = calc.add_sheet(self.proj, name="Data")
        assert sheet["name"] == "Data"
        assert len(self.proj["sheets"]) == 2

    def test_remove_sheet(self):
        calc.add_sheet(self.proj, name="Extra")
        calc.remove_sheet(self.proj, 1)
        assert len(self.proj["sheets"]) == 1

    def test_rename_sheet(self):
        calc.rename_sheet(self.proj, 0, "Renamed")
        assert self.proj["sheets"][0]["name"] == "Renamed"

    def test_set_cell(self):
        result = calc.set_cell(self.proj, "A1", "Hello")
        assert result["ref"] == "A1"
        assert result["value"] == "Hello"

    def test_set_cell_float(self):
        result = calc.set_cell(self.proj, "B2", "42.5")
        assert result["type"] == "float"

    def test_set_cell_formula(self):
        result = calc.set_cell(self.proj, "C3", "0", formula="=SUM(A1:A10)")
        assert result["formula"] == "=SUM(A1:A10)"

    def test_get_cell(self):
        calc.set_cell(self.proj, "A1", "test")
        result = calc.get_cell(self.proj, "A1")
        assert result["value"] == "test"

    def test_get_cell_empty(self):
        result = calc.get_cell(self.proj, "Z99")
        assert result["value"] is None

    def test_clear_cell(self):
        calc.set_cell(self.proj, "A1", "test")
        calc.clear_cell(self.proj, "A1")
        result = calc.get_cell(self.proj, "A1")
        assert result["value"] is None

    def test_set_range(self):
        result = calc.set_range(self.proj, "B2", [["a", "b"], ["c", "d"]])
        assert result["cells_set"] == 4

    def test_merge_cells(self):
        result = calc.merge_cells(self.proj, "A1", "D4")
        assert result["start"] == "A1"
        assert result["end"] == "D4"

    def test_list_sheets(self):
        sheets = calc.list_sheets(self.proj)
        assert len(sheets) == 1
        assert sheets[0]["name"] == "Sheet1"

    def test_invalid_cell_ref(self):
        with pytest.raises(ValueError):
            calc.set_cell(self.proj, "INVALID", "val")


class TestImpressContent:
    """测试 Impress 演示文稿编辑。"""

    def setup_method(self):
        self.proj = document.create_document(doc_type="impress", name="test")

    def test_add_slide(self):
        slide = impress.add_slide(self.proj, title="Slide 1", content="Body")
        assert slide["title"] == "Slide 1"
        assert len(self.proj["slides"]) == 1

    def test_remove_slide(self):
        impress.add_slide(self.proj, title="A")
        impress.add_slide(self.proj, title="B")
        impress.remove_slide(self.proj, 0)
        assert len(self.proj["slides"]) == 1
        assert self.proj["slides"][0]["title"] == "B"

    def test_set_slide_content(self):
        impress.add_slide(self.proj, title="Old")
        impress.set_slide_content(self.proj, 0, title="New", content="Updated")
        assert self.proj["slides"][0]["title"] == "New"
        assert self.proj["slides"][0]["content"] == "Updated"

    def test_add_element(self):
        impress.add_slide(self.proj, title="Slide")
        elem = impress.add_slide_element(
            self.proj, 0, element_type="text_box", text="Hello",
        )
        assert elem["type"] == "text_box"
        assert elem["text"] == "Hello"

    def test_remove_element(self):
        impress.add_slide(self.proj, title="Slide")
        impress.add_slide_element(self.proj, 0, element_type="text_box", text="A")
        impress.add_slide_element(self.proj, 0, element_type="text_box", text="B")
        impress.remove_slide_element(self.proj, 0, 0)
        elements = self.proj["slides"][0]["elements"]
        assert len(elements) == 1

    def test_move_slide(self):
        impress.add_slide(self.proj, title="A")
        impress.add_slide(self.proj, title="B")
        impress.move_slide(self.proj, 0, 1)
        assert self.proj["slides"][0]["title"] == "B"

    def test_duplicate_slide(self):
        impress.add_slide(self.proj, title="Original")
        impress.duplicate_slide(self.proj, 0)
        assert len(self.proj["slides"]) == 2
        assert "副本" in self.proj["slides"][1]["title"]

    def test_list_slides(self):
        impress.add_slide(self.proj, title="A")
        impress.add_slide(self.proj, title="B")
        slides = impress.list_slides(self.proj)
        assert len(slides) == 2


class TestStyles:
    """测试样式管理。"""

    def setup_method(self):
        self.proj = document.create_document(doc_type="writer", name="test")

    def test_create_style(self):
        result = styles.create_style(
            self.proj, name="MyStyle", family="paragraph",
            properties={"font_size": "14pt", "bold": True},
        )
        assert result["name"] == "MyStyle"
        assert self.proj["styles"]["MyStyle"]["properties"]["bold"] is True

    def test_modify_style(self):
        styles.create_style(self.proj, name="S", properties={"font_size": "12pt"})
        styles.modify_style(self.proj, "S", properties={"font_size": "16pt"})
        assert self.proj["styles"]["S"]["properties"]["font_size"] == "16pt"

    def test_remove_style(self):
        styles.create_style(self.proj, name="S", properties={})
        styles.remove_style(self.proj, "S")
        assert "S" not in self.proj["styles"]

    def test_list_styles(self):
        styles.create_style(self.proj, name="A", properties={})
        styles.create_style(self.proj, name="B", properties={})
        result = styles.list_styles(self.proj)
        assert len(result) == 2

    def test_invalid_property(self):
        with pytest.raises(ValueError):
            styles.create_style(self.proj, name="S", properties={"bad_prop": 1})

    def test_apply_style(self):
        styles.create_style(self.proj, name="Big", properties={"font_size": "18pt"})
        writer.add_paragraph(self.proj, text="test")
        styles.apply_style(self.proj, "Big", 0)
        assert self.proj["content"][0]["style"]["font_size"] == "18pt"


class TestSession:
    """测试会话管理。"""

    def test_session_init(self):
        sess = Session()
        assert not sess.has_project()

    def test_set_project(self):
        sess = Session()
        proj = document.create_document(doc_type="writer", name="test")
        sess.set_project(proj, "/tmp/test.json")
        assert sess.has_project()
        assert sess.project_path == "/tmp/test.json"

    def test_no_project_error(self):
        sess = Session()
        with pytest.raises(RuntimeError):
            sess.get_project()

    def test_snapshot_and_undo(self):
        sess = Session()
        proj = document.create_document(doc_type="writer", name="original")
        sess.set_project(proj)

        sess.snapshot("before change")
        sess.get_project()["name"] = "changed"
        assert sess.get_project()["name"] == "changed"

        desc = sess.undo()
        assert "before change" in desc
        assert sess.get_project()["name"] == "original"

    def test_redo(self):
        sess = Session()
        proj = document.create_document(doc_type="writer", name="original")
        sess.set_project(proj)

        sess.snapshot("change")
        sess.get_project()["name"] = "changed"
        sess.undo()
        sess.redo()
        assert sess.get_project()["name"] == "changed"

    def test_save_session(self, tmp_path):
        sess = Session()
        proj = document.create_document(doc_type="writer", name="save_test")
        path = os.path.join(tmp_path, "session_test.json")
        sess.set_project(proj, path)
        result = sess.save_session()
        assert os.path.exists(result)

    def test_status(self):
        sess = Session()
        proj = document.create_document(doc_type="calc", name="mydata")
        sess.set_project(proj)
        status = sess.status()
        assert status["has_project"]
        assert status["document_name"] == "mydata"
        assert status["document_type"] == "calc"
        assert not status["modified"]

    def test_history(self):
        sess = Session()
        proj = document.create_document(doc_type="writer", name="test")
        sess.set_project(proj)

        sess.snapshot("step 1")
        sess.get_project()["name"] = "v1"
        sess.snapshot("step 2")
        sess.get_project()["name"] = "v2"

        history = sess.list_history()
        assert len(history) == 2
