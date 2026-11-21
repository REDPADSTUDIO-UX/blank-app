"""Runtime control regressions, using synthetic transport packets only."""
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from tests.test_cpu_creative import response, Response
from redpad_pipeline.screenwriter import LocalWriter, WritingError
from redpad_pipeline.staged_writing import StagedDraft, obj, text_schema


class LocalThinkingTests(unittest.TestCase):
    def test_explicit_false_is_sent_and_unsupported_control_fails_closed(self):
        writer=LocalWriter('fixture:local',think=False)
        meta={'thinking':{'values':[False,True],'default':True}}
        reply={'done':True,'message':{'content':'{"ok":true}'}}
        with patch('urllib.request.OpenerDirector.open',side_effect=[response(meta),response(reply)]) as transport:
            self.assertEqual(writer('system','prompt'),{'ok':True})
            self.assertIs(json.loads(transport.call_args.args[0].data)['think'],False)
        with patch('urllib.request.OpenerDirector.open',return_value=response({})) as transport:
            with self.assertRaises(WritingError):writer('system','prompt')
            self.assertEqual(transport.call_count,1)
        for bad in (0,1,'false',[]):
            with self.assertRaises(WritingError):LocalWriter('fixture:local',think=bad)

    def test_default_payload_unchanged_and_thinking_is_separate_from_final_json(self):
        writer=LocalWriter('fixture:local',stream=True)
        packets=[{'message':{'thinking':'MODEL reasoning fixture'}},
                 {'message':{'content':'{"ok":true}'},'done':True,'done_reason':'stop'}]
        stream=Response(('\n'.join(json.dumps(p) for p in packets)+'\n').encode())
        with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),stream]) as transport:
            self.assertEqual(writer('system','prompt'),{'ok':True})
            self.assertNotIn('think',json.loads(transport.call_args.args[0].data))
        self.assertEqual(writer.last_thinking_output,'MODEL reasoning fixture')
        self.assertEqual(writer.last_raw_output,'{"ok":true}')
        self.assertEqual(writer.last_evidence['thinking_sha256'],hashlib.sha256(writer.last_thinking_output.encode()).hexdigest())

    def test_token_exhaustion_preserves_runtime_thinking_and_never_accepts(self):
        with tempfile.TemporaryDirectory() as d:
            writer=LocalWriter('fixture:local',stream=True,think=False)
            packet={'message':{'thinking':'fixture partial'},'done':True,'done_reason':'length'}
            stream=Response((json.dumps(packet)+'\n').encode())
            with patch('urllib.request.OpenerDirector.open',side_effect=[response({'thinking':{'values':[False,True]}}),stream]):
                record=StagedDraft(d).run('story','story',{},'test',obj({'text':text_schema()}),complete=writer,think=False)
            self.assertEqual(record['status'],'failed')
            self.assertEqual(record['runtime_thinking'],'fixture partial')
            self.assertIs(record['request']['think'],False)
            self.assertFalse(record['evidence']['inference_completed'])

    def test_thinking_mode_changes_stage_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            lab=StagedDraft(d);args=('story','story',{},'test',obj({'text':text_schema()}))
            lab.run(*args,complete=lambda *_:{'text':'fixture'})
            with self.assertRaises(WritingError):lab.run(*args,think=False,complete=lambda *_:{'text':'fixture'})
