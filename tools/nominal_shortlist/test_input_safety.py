"""Synthetic input/output safety tests; no physical measurements are used."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from shortlist_transfer import load, protect_input_path, write_json_atomic

VALID = 'module,Source,Target\nA,100,100\nB,90,95\n'
SCRIPT = Path(__file__).with_name('shortlist_transfer.py')


class InputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'synthetic.csv'
        self.source.write_text(VALID, encoding='utf-8')
        self.output = self.root / 'result.json'

    def run_cli(self, output=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--input', str(self.source),
             '--source', 'Source', '--target', 'Target', '--output', str(output or self.output)],
            capture_output=True, text=True, check=False)

    def test_extra_fields_rejected(self):
        self.source.write_text('module,Source,Target\nA,100,100,unexpected\n')
        with self.assertRaises(ValueError):
            load(self.source, 'Source', 'Target', set())

    def test_missing_unselected_field_rejected(self):
        self.source.write_text('module,Source,Target,Note\nA,100,100\n')
        with self.assertRaises(ValueError):
            load(self.source, 'Source', 'Target', set())

    def test_malformed_quote_rejected(self):
        self.source.write_text('module,Source,Target\nA,100,"100\n')
        with self.assertRaises(csv.Error):
            load(self.source, 'Source', 'Target', set())

    def test_blank_or_padded_headers_rejected(self):
        for headers in ('module,Source,Target,', 'module,Source,Target, Source'):
            with self.subTest(headers=headers):
                self.source.write_text(headers + '\nA,100,100,x\n')
                with self.assertRaises(ValueError):
                    load(self.source, 'Source', 'Target', set())

    def test_identifier_cannot_be_an_endpoint(self):
        self.source.write_text('module,Target\n1,100\n')
        with self.assertRaises(ValueError):
            load(self.source, 'module', 'Target', set())

    def test_identical_input_output_preserved(self):
        before = self.source.read_bytes()
        result = self.run_cli(self.source)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.source.read_bytes(), before)

    def test_resolved_alias_rejected(self):
        with self.assertRaises(ValueError):
            protect_input_path(self.source, self.root / '.' / 'synthetic.csv')

    def test_symlink_alias_preserves_input(self):
        alias = self.root / 'alias.json'
        try:
            alias.symlink_to(self.source)
        except (OSError, NotImplementedError) as error:
            self.skipTest(str(error))
        before = self.source.read_bytes()
        result = self.run_cli(alias)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertTrue(alias.is_symlink())

    def test_hardlink_alias_preserves_input(self):
        alias = self.root / 'hardlink.json'
        try:
            os.link(self.source, alias)
        except (OSError, NotImplementedError) as error:
            self.skipTest(str(error))
        before = self.source.read_bytes()
        result = self.run_cli(alias)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(alias.read_bytes(), before)

    def test_output_symlink_to_another_file_rejected(self):
        other = self.root / 'other.txt'
        other.write_text('do not replace')
        try:
            self.output.symlink_to(other)
        except (OSError, NotImplementedError) as error:
            self.skipTest(str(error))
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(other.read_text(), 'do not replace')

    def test_invalid_input_preserves_previous_result(self):
        self.output.write_bytes(b'previous result\n')
        self.source.write_text('module,Source,Target\nA,100,100,extra\n')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')

    def test_invalid_encoding_is_controlled_rejection(self):
        self.source.write_bytes(b'\xff\xfeinvalid')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('INPUT REJECTED', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(self.output.exists())

    def test_unrepresentable_display_number_rejected_without_output(self):
        self.source.write_text('module,Source,Target\nA,1e999,100\n')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(self.output.exists())

    def test_serialization_failure_does_not_damage_result(self):
        self.output.write_bytes(b'previous result\n')
        with self.assertRaises(ValueError):
            write_json_atomic(self.output, {'invalid': float('nan')})
        self.assertEqual(self.output.read_bytes(), b'previous result\n')
        self.assertEqual(list(self.root.glob('.shortlist-*.tmp')), [])

    def test_replace_failure_cleans_temporary_and_preserves_result(self):
        self.output.write_bytes(b'previous result\n')
        with patch('shortlist_transfer.os.replace', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError):
                write_json_atomic(self.output, {'valid': 1})
        self.assertEqual(self.output.read_bytes(), b'previous result\n')
        self.assertEqual(list(self.root.glob('.shortlist-*.tmp')), [])

    def test_valid_quoted_identifiers_and_extra_named_columns(self):
        self.source.write_text('module,Source,Target,Note\n"A, quoted",100,100,"x,y"\nB,90,95,\n\n')
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text())['false_exclusions'], ['B'])
        self.assertEqual(list(self.root.glob('.shortlist-*.tmp')), [])

    def test_output_directory_failure_does_not_damage_input(self):
        self.output.mkdir()
        before = self.source.read_bytes()
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.root.glob('.shortlist-*.tmp')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
