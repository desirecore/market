#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["lxml>=5.3,<7", "defusedxml>=0.7"]
# ///
"""内置 Office 技能的离线 Schema 与中文 XML 回归，不访问网络。"""

from __future__ import annotations

import builtins
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
OFFICE_SKILLS = ("docx", "pptx", "xlsx")
XSD = "{http://www.w3.org/2001/XMLSchema}"
WORD_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>离线中文文档</w:t></w:r></w:p></w:body>
</w:document>'''
CORE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>离线中文文档</dc:title>
 <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-14T00:00:00Z</dcterms:created>
</cp:coreProperties>'''


class RejectRemoteSchema(etree.Resolver):
    def resolve(self, url, public_id, context):
        if urlsplit(url).scheme not in ("", "file") and not Path(url).is_absolute():
            raise OSError(f"离线 Schema 不允许远程依赖：{url}")
        return None


def offline_parser():
    parser = etree.XMLParser(no_network=True)
    parser.resolvers.add(RejectRemoteSchema())
    return parser


def load_docx_validator(skill: str):
    directory = ROOT / "skills" / skill / "scripts" / "office" / "validators"
    name = f"market_office_{skill}_validators"
    spec = importlib.util.spec_from_file_location(
        name, directory / "__init__.py", submodule_search_locations=[str(directory)]
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module.DOCXSchemaValidator


class OfflineOfficeResourcesTests(unittest.TestCase):
    def test_all_builtin_schemas_have_local_dependencies_and_compile_offline(self):
        builtin_ids = json.loads((ROOT / "builtin-skills.json").read_text(encoding="utf-8"))["skills"]
        checked = 0
        for skill in builtin_ids:
            skill_root = ROOT / "skills" / skill
            for schema in sorted(skill_root.rglob("*.xsd")):
                with self.subTest(schema=str(schema.relative_to(ROOT))):
                    document = etree.parse(str(schema), offline_parser())
                    for node in document.iter():
                        if node.tag not in (XSD + "import", XSD + "include", XSD + "redefine"):
                            continue
                        location = node.get("schemaLocation")
                        if location is None:
                            continue
                        self.assertEqual(urlsplit(location).scheme, "", location)
                        target = (schema.parent / location).resolve()
                        self.assertTrue(target.is_relative_to(skill_root.resolve()), location)
                        self.assertTrue(target.is_file(), location)
                    etree.XMLSchema(document)
                    checked += 1
        self.assertGreater(checked, 0, "不能在未发现任何 Schema 时静默通过")

    def test_chinese_document_and_dublin_core_validate_with_gbk_default(self):
        # 模拟 Windows GBK 默认文本读取，避免只在 UTF-8 的 CI 上掩盖回归。
        original_open = builtins.open

        def gbk_open(file, mode="r", *args, **kwargs):
            if "b" not in mode and not args and "encoding" not in kwargs:
                kwargs["encoding"] = "gbk"
            return original_open(file, mode, *args, **kwargs)

        for skill in OFFICE_SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                word = directory / "word" / "document.xml"
                core = directory / "docProps" / "core.xml"
                word.parent.mkdir()
                core.parent.mkdir()
                word.write_bytes(WORD_XML.encode("utf-8"))
                core.write_bytes(CORE_XML.encode("utf-8"))
                validator = load_docx_validator(skill)(directory)
                with patch("builtins.open", side_effect=gbk_open):
                    for file in (word, core):
                        valid, errors = validator._validate_single_file_xsd(file, directory)
                        self.assertTrue(valid, errors)

                # 保留真实 XSD 校验，不能用跳过/放宽校验来实现“通过”。
                word.write_bytes(WORD_XML.replace("<w:p>", "<w:unknown>").replace("</w:p>", "</w:unknown>").encode("utf-8"))
                valid, errors = validator._validate_single_file_xsd(word, directory)
                self.assertFalse(valid)
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
