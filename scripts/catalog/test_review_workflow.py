#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""受信任邀请审核流程不能执行 PR 来源代码或将未知 422 当作审核成功。"""
from pathlib import Path
import unittest
import yaml


class ReviewWorkflowTests(unittest.TestCase):
    def test_request_has_write_context_without_pr_code_execution(self):
        path = Path(__file__).resolve().parents[2] / '.github/workflows/auto-request-copilot-review.yml'
        text = path.read_text()
        workflow = yaml.load(text, Loader=yaml.BaseLoader)
        self.assertIn('pull_request_target', workflow['on'])
        self.assertNotIn('pull_request', workflow['on'])
        self.assertEqual(workflow['permissions']['pull-requests'], 'write')
        for step in workflow['jobs']['request']['steps']:
            self.assertNotIn('uses', step)
            script = step.get('run', '')
            self.assertNotIn('checkout', script)
            self.assertNotIn('pull_request.head', script)
            self.assertNotIn('pull_request.title', script)
            self.assertNotIn('pull_request.body', script)
        self.assertIn('/reviews', text)
        self.assertNotIn('likely already reviewed', text)


if __name__ == '__main__': unittest.main()
