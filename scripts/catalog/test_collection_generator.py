#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Unit tests for collection generation check mode."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


GENERATOR_PATH = Path(__file__).parents[1] / "gen-collection-children.py"
SPEC = importlib.util.spec_from_file_location("market_collection_generator", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
GENERATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GENERATOR
SPEC.loader.exec_module(GENERATOR)


class CollectionGeneratorCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.skills_dir = Path(self.tempdir.name) / "skills"
        self.entry_path = self.skills_dir / "example-collection" / "entry.json"
        self.entry_path.parent.mkdir(parents=True)
        self.children = [{"id": "child-one", "path": "skills/child-one"}]
        self.write_entry(self.children)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_entry(self, children: list[dict[str, str]]) -> None:
        self.entry_path.write_text(
            json.dumps(
                {
                    "id": "example-collection",
                    "source": {
                        "kind": "git",
                        "repoUrl": "https://example.com/example.git",
                        "repoBranch": "main",
                        "ref": "a" * 40,
                    },
                    "children": children,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def run_check(self, discovered: list[dict[str, str]]) -> bool:
        before = self.entry_path.read_bytes()
        with (
            patch.object(GENERATOR, "SKILLS_DIR", self.skills_dir),
            patch.object(GENERATOR, "clone_pinned"),
            patch.object(GENERATOR, "discover_children", return_value=discovered),
        ):
            result = GENERATOR.process("example-collection", check=True)
        self.assertEqual(before, self.entry_path.read_bytes(), "--check must never write entry.json")
        return result

    def test_check_accepts_current_children_without_writing(self) -> None:
        self.assertTrue(self.run_check(self.children))

    def test_check_rejects_stale_children_without_writing(self) -> None:
        self.assertFalse(self.run_check([{"id": "child-two", "path": "skills/child-two"}]))

    def test_check_rejects_collection_source_path(self) -> None:
        entry = json.loads(self.entry_path.read_text(encoding="utf-8"))
        entry["source"]["path"] = "skills"
        self.entry_path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
        self.assertFalse(self.run_check(self.children))

    def test_check_skips_unpinned_collection_without_network_or_writes(self) -> None:
        entry = json.loads(self.entry_path.read_text(encoding="utf-8"))
        del entry["source"]["ref"]
        self.entry_path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
        before = self.entry_path.read_bytes()
        with (
            patch.object(GENERATOR, "SKILLS_DIR", self.skills_dir),
            patch.object(GENERATOR, "clone_pinned") as clone,
        ):
            self.assertTrue(GENERATOR.process("example-collection", check=True))
        clone.assert_not_called()
        self.assertEqual(before, self.entry_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
