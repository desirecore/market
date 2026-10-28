#!/usr/bin/env python3
"""Standalone Office launcher contracts; standard library only, no installs/network.

Run: python -B scripts/office/test_runtime_launcher.py
"""

import contextlib
import io
from itertools import product
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ("pptx", "xlsx")


class RuntimeLauncherTests(unittest.TestCase):
    def fixture(self, skill, directory):
        scripts = Path(directory) / "isolated home 中文" / "skills" / skill / "scripts"
        scripts.mkdir(parents=True)
        launcher = scripts / "with-deps.py"
        shutil.copyfile(ROOT / "skills" / skill / "scripts" / launcher.name, launcher)
        module = types.ModuleType("launcher_" + skill)
        module.__file__ = str(launcher)
        # Avoid writing a .pyc beside the repository's installed skill.
        exec(compile(launcher.read_bytes(), str(launcher), "exec"), module.__dict__)
        target = scripts / "office" / "probe.py"
        target.parent.mkdir()
        target.write_text("raise SystemExit(0)\n", encoding="utf-8")
        libs = Path(module._PYLIBS)
        libs.mkdir(parents=True)
        return module, launcher, target, libs

    def test_relative_target_arguments_environment_and_cwd_are_preserved(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, target, libs = self.fixture(skill, directory)
                before = os.getcwd()
                with patch.object(sys, "argv", [str(launcher), "office/probe.py", "file with spaces", "中文", "--validate", "false"]), \
                        patch.dict(os.environ, {"PYTHONPATH": "existing-path"}), \
                        patch.object(module.subprocess, "run", return_value=types.SimpleNamespace(returncode=17)) as run:
                    self.assertEqual(module.main(), 17)
                command = run.call_args.args[0]
                self.assertEqual(command[:2], [sys.executable, "-B"])
                self.assertEqual(Path(command[2]), target)
                self.assertEqual(command[3:], ["file with spaces", "中文", "--validate", "false"])
                self.assertEqual(run.call_args.kwargs["env"]["PYTHONPATH"], str(libs) + os.pathsep + "existing-path")
                self.assertEqual(run.call_args.kwargs["env"]["PYTHONDONTWRITEBYTECODE"], "1")
                self.assertNotIn("cwd", run.call_args.kwargs)
                self.assertNotIn("shell", run.call_args.kwargs)
                self.assertEqual(os.getcwd(), before)

    def test_absolute_target_prefers_prepared_interpreter(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, target, _libs = self.fixture(skill, directory)
                bundled = Path(module._BUNDLED)
                bundled.parent.mkdir(parents=True)
                bundled.write_bytes(b"fixture executable; subprocess is mocked")
                with patch.object(sys, "argv", [str(launcher), str(target)]), \
                        patch.object(module.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)) as run:
                    self.assertEqual(module.main(), 0)
                self.assertEqual(run.call_args.args[0], [str(bundled), "-B", str(target)])

    def test_current_python_option_keeps_external_packages_interpreter(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, target, _libs = self.fixture(skill, directory)
                bundled = Path(module._BUNDLED)
                bundled.parent.mkdir(parents=True)
                bundled.write_bytes(b"fixture executable; subprocess is mocked")
                with patch.object(sys, "argv", [str(launcher), "--current-python", "office/probe.py", "output.pptx"]), \
                        patch.object(module.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)) as run:
                    self.assertEqual(module.main(), 0)
                command = run.call_args.args[0]
                self.assertEqual(command[:2], [sys.executable, "-B"])
                self.assertEqual(Path(command[2]), target)
                self.assertEqual(command[3:], ["output.pptx"])

    def test_current_python_never_silently_uses_python_39(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, _target, _libs = self.fixture(skill, directory)
                with patch.object(sys, "argv", [str(launcher), "office/probe.py"]), \
                        patch.object(sys, "version_info", (3, 9, 0)), \
                        patch.object(module.subprocess, "run") as run, contextlib.redirect_stderr(io.StringIO()) as error:
                    self.assertEqual(module.main(), 1)
                run.assert_not_called()
                self.assertIn("Python 3.10+", error.getvalue())

    def test_old_bootstrap_can_start_prepared_interpreter(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, _target, _libs = self.fixture(skill, directory)
                bundled = Path(module._BUNDLED)
                bundled.parent.mkdir(parents=True)
                bundled.write_bytes(b"fixture executable; subprocess is mocked")
                with patch.object(sys, "argv", [str(launcher), "office/probe.py"]), \
                        patch.object(sys, "version_info", (3, 9, 0)), \
                        patch.object(module.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)) as run:
                    self.assertEqual(module.main(), 0)
                self.assertEqual(run.call_args.args[0][0], str(bundled))

    def test_only_process_start_failure_can_fall_back(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, _target, _libs = self.fixture(skill, directory)
                bundled = Path(module._BUNDLED)
                bundled.parent.mkdir(parents=True)
                bundled.write_bytes(b"fixture executable; subprocess is mocked")
                with patch.object(sys, "argv", [str(launcher), "office/probe.py"]), \
                        patch.object(module.subprocess, "run", side_effect=[OSError("fixture start failure"), types.SimpleNamespace(returncode=7)]) as run, \
                        contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(module.main(), 7)
                self.assertEqual(run.call_count, 2)
                self.assertEqual(run.call_args_list[1].args[0][0], sys.executable)

    def test_failed_prepared_start_cannot_fall_back_to_python_39(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                module, launcher, _target, _libs = self.fixture(skill, directory)
                bundled = Path(module._BUNDLED)
                bundled.parent.mkdir(parents=True)
                bundled.write_bytes(b"fixture executable; subprocess is mocked")
                with patch.object(sys, "argv", [str(launcher), "office/probe.py"]), \
                        patch.object(sys, "version_info", (3, 9, 0)), \
                        patch.object(module.subprocess, "run", side_effect=OSError("fixture start failure")) as run, \
                        contextlib.redirect_stderr(io.StringIO()) as error:
                    self.assertEqual(module.main(), 1)
                run.assert_called_once()
                self.assertIn("Python 3.10+", error.getvalue())

    def test_target_failures_and_signals_are_not_replayed_or_success(self):
        for skill in SKILLS:
            for code in (1, 126, 127, -9):
                with self.subTest(skill=skill, code=code), tempfile.TemporaryDirectory() as directory:
                    module, launcher, _target, _libs = self.fixture(skill, directory)
                    bundled = Path(module._BUNDLED)
                    bundled.parent.mkdir(parents=True)
                    bundled.write_bytes(b"fixture executable; subprocess is mocked")
                    with patch.object(sys, "argv", [str(launcher), "office/probe.py"]), \
                            patch.object(module.subprocess, "run", return_value=types.SimpleNamespace(returncode=code)) as run:
                        self.assertEqual(module.main(), code)
                    run.assert_called_once()

    def test_missing_target_or_option_without_target_has_no_side_effect(self):
        for skill in SKILLS:
            for arguments in ([], ["--current-python"], ["office/missing.py"]):
                with self.subTest(skill=skill, arguments=arguments), tempfile.TemporaryDirectory() as directory:
                    module, launcher, _target, _libs = self.fixture(skill, directory)
                    with patch.object(sys, "argv", [str(launcher), *arguments]), \
                            patch.object(module.subprocess, "run") as run, contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(module.main(), 2)
                    run.assert_not_called()

    def test_independently_installed_skill_resolves_own_libs_without_bytecode(self):
        for skill, current_python in product(SKILLS, (False, True)):
            with self.subTest(skill=skill, current_python=current_python), tempfile.TemporaryDirectory() as directory:
                module, launcher, target, libs = self.fixture(skill, directory)
                if current_python:
                    bundled = Path(module._BUNDLED)
                    bundled.parent.mkdir(parents=True)
                    bundled.write_bytes(b"must not be executed with --current-python")
                (libs / "launcher_fixture_dependency.py").write_text("value = 'from prepared libs'\n", encoding="utf-8")
                (target.parent / "local_helper.py").write_text("value = 'script directory'\n", encoding="utf-8")
                target.write_text(
                    "import json, os, sys, launcher_fixture_dependency, local_helper\n"
                    "print(json.dumps({'argv': sys.argv[1:], 'name': __name__, 'cwd': os.getcwd(), "
                    "'dependency': launcher_fixture_dependency.__file__, 'local': local_helper.value}))\n",
                    encoding="utf-8",
                )
                environment = dict(os.environ)
                environment.pop("PYTHONPATH", None)
                environment["PYTHONNOUSERSITE"] = "1"
                completed = subprocess.run(
                    [sys.executable, "-B", str(launcher), *(["--current-python"] if current_python else []), "office/probe.py", "spaced input", "中文"],
                    cwd=directory, env=environment, capture_output=True, text=True, check=True,
                )
                self.assertEqual(completed.stderr, "")
                result = json.loads(completed.stdout)
                self.assertEqual(result["argv"], ["spaced input", "中文"])
                self.assertEqual(result["name"], "__main__")
                self.assertEqual(Path(result["cwd"]).resolve(), Path(directory).resolve())
                self.assertEqual(Path(result["dependency"]).resolve(), (libs / "launcher_fixture_dependency.py").resolve())
                self.assertEqual(result["local"], "script directory")
                self.assertFalse(list(Path(directory).rglob("*.pyc")))

    def test_missing_dependency_is_a_real_nonzero_target_failure(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                _module, launcher, target, _libs = self.fixture(skill, directory)
                target.write_text("import unavailable_office_test_dependency_5335\n", encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, "-B", str(launcher), "office/probe.py"],
                    cwd=directory, capture_output=True, text=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("ModuleNotFoundError", completed.stderr)


if __name__ == "__main__":
    unittest.main()
