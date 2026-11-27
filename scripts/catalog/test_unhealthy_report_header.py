"""Regression checks for the report timestamp and Actions attempt link."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from unhealthy_report import START, main, managed_body, report_header, sync_plan


class ReportHeaderTests(unittest.TestCase):
    def test_midnight_rollover_and_exact_attempt(self):
        env = {
            'GITHUB_SERVER_URL': 'https://github.com',
            'GITHUB_REPOSITORY': 'desirecore/market',
            'GITHUB_RUN_ID': '45922584295',
            'GITHUB_RUN_ATTEMPT': '2',
        }
        header = report_header(datetime(2026, 11, 26, 23, 59, 1, tzinfo=timezone.utc), env)
        self.assertIn('2026-11-27 07:59:01 (UTC+08:00)', header)
        self.assertIn('https://github.com/desirecore/market/actions/runs/45922584295/attempts/2', header)
        self.assertTrue(managed_body('', header + '\n\nReport').startswith(START + '\n' + header))

    def test_no_actions_context_has_time_without_a_link(self):
        header = report_header(datetime(2026, 11, 27, 2, 1, tzinfo=timezone.utc), {})
        self.assertIn('2026-11-27 10:01:00 (UTC+08:00)', header)
        self.assertNotIn('Workflow run', header)

    def test_cli_places_header_first_and_links_to_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'report.md'
            args = ['unhealthy_report.py', '--output', str(output), '--complete']
            for name in ('results', 'coverage', 'tracked'):
                path = root / (name + '.json')
                path.write_text('[]')
                args.extend(['--' + name, str(path)])
            env = {'GITHUB_REPOSITORY': 'desirecore/market', 'GITHUB_RUN_ID': '123'}
            with patch.dict(os.environ, env, clear=True), patch.object(sys, 'argv', args):
                main()
            first = output.read_text().splitlines()[0]
            self.assertIn('Report generated (Beijing time):', first)
            self.assertIn('https://github.com/desirecore/market/actions/runs/123)', first)

    def test_unchanged_rerun_skips_body_edit_but_preserves_state_transitions(self):
        old = report_header(datetime(2026, 11, 27, 2, 1, tzinfo=timezone.utc), {
            'GITHUB_REPOSITORY': 'desirecore/market', 'GITHUB_RUN_ID': '123',
        })
        new = report_header(datetime(2026, 11, 28, 2, 1, tzinfo=timezone.utc), {
            'GITHUB_REPOSITORY': 'desirecore/market', 'GITHUB_RUN_ID': '456',
        })
        body = managed_body('', old + '\n\nSame findings')
        rerun = new + '\n\nSame findings'
        self.assertEqual(sync_plan({'body': body, 'state': 'open'}, rerun, True, True), {})
        self.assertEqual(sync_plan({'body': body, 'state': 'closed'}, rerun, True, True), {'state': 'open'})
        self.assertEqual(sync_plan({'body': body, 'state': 'open'}, rerun, False, True),
                         {'state': 'closed', 'state_reason': 'completed'})

    def test_existing_headerless_report_gets_a_header(self):
        header = report_header(datetime(2026, 11, 27, 2, 1, tzinfo=timezone.utc), {})
        issue = {'body': managed_body('', 'Same findings'), 'state': 'open'}
        edits = sync_plan(issue, header + '\n\nSame findings', True, True)
        self.assertIn(START + '\n' + header, edits['body'])

    def test_changed_findings_publish_new_header_and_preserve_archived_text(self):
        old = report_header(datetime(2026, 11, 27, 2, 1, tzinfo=timezone.utc), {})
        new = report_header(datetime(2026, 11, 28, 2, 1, tzinfo=timezone.utc), {})
        body = managed_body('Archived text', old + '\n\nOld findings')
        edits = sync_plan({'body': body, 'state': 'open'}, new + '\n\nNew findings', True, True)
        self.assertIn(START + '\n' + new, edits['body'])
        self.assertNotIn(old, edits['body'])
        self.assertIn('Archived text', edits['body'])
