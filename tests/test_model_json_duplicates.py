"""Actual Director output exposed repeated fields; these are software regressions."""
import json
import unittest
from unittest.mock import patch
from redpad_pipeline.screenwriter import LocalWriter, WritingError, model_json
from redpad_pipeline.kaggle_benchmark import cases, technical_validation
from tests.test_phase3 import response


class DuplicateModelJSONTests(unittest.TestCase):
    def test_nested_fields_do_not_silently_replace_direction(self):
        with self.assertRaisesRegex(WritingError, 'Duplicate JSON'):
            model_json('{"scenes":[{"performance":"locked","performance":"changed"}]}')
        self.assertEqual(model_json('[{"camera":"a"},{"camera":"b"}]'),[{'camera':'a'},{'camera':'b'}])

    def test_duplicate_findings_cannot_hide_a_false_accusation(self):
        case=next(c for c in cases()['cases'] if c['id']=='clean_abstention')
        raw='{"findings":[{"code":"invented"}],"findings":[]}'
        self.assertEqual(json.loads(raw),{'findings':[]})  # Old lossy decoding.
        self.assertFalse(technical_validation(case,raw,{'truncated':False})['technical_pass'])

    def test_local_writer_preserves_ambiguous_raw_without_fallback(self):
        raw='{"scenes":[{"continuity":"locked","continuity":"changed"}]}'
        writer=LocalWriter('fixture:local')
        with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),response({'done':True,'done_reason':'stop','message':{'content':raw}})]) as transport:
            with self.assertRaisesRegex(WritingError,'Duplicate JSON'):writer('system','prompt')
        self.assertEqual(writer.last_raw_output,raw)
        self.assertEqual(transport.call_count,2)
