"""Authored native receipt/PCM fixtures only; no inference or real human review."""
import copy
import json
import socket
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from redpad_pipeline.agents import AgentStore,AgentError,encode
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.native_execution import NativeExecution
from redpad_pipeline.native_local_bundle import NativeInstalls
from redpad_pipeline.offline_preparation import PreparedRequests
from redpad_pipeline.no_gpu_staging import StagingLedger,load
from redpad_pipeline.professional_readiness import ProfessionalLab,file_sha,trial_context
from tests.test_agent_foundation import fixture

REAL_SOCKET=socket.socket


class NativeProfessionalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3')
        self.engine=Engine(self.store);self.lab=ProfessionalLab(self.store);self.native=NativeExecution(self.store)
        self.trial=self.lab.plan('voice',['pinned/indic_speak'],
            'Check exact native worker binding using authored receipt fixtures, without launching any model.',
            'Capture immutable PCM bytes and refuse synthetic-worker evidence.',max_calls=1)
        self.run=self.engine.enqueue('voice',fixture('voice'))
        p=load()[0]['profiles']['indic_speak']
        self.install={'repo':p['repo'],'revision':p['revision']}
        self.stage={'id':'stage','context':{'role':'voice','run':self.run,'source_revisions':[]}}
        self.prepared={'profile':'indic_speak','stage_id':'stage'}
        for target,value in [(PreparedRequests,self.prepared),(StagingLedger,self.stage),(NativeInstalls,self.install)]:
            mock=patch.object(target,'get',return_value=value);mock.start();self.addCleanup(mock.stop)
        def local_socket(family=socket.AF_INET,*args,**kwargs):
            if family!=socket.AF_UNIX:raise AssertionError('NO NETWORK SOCKETS')
            return REAL_SOCKET(family,*args,**kwargs)
        mock=patch('socket.socket',side_effect=local_socket);mock.start();self.addCleanup(mock.stop)
        for target in ('subprocess.Popen','redpad_pipeline.kaggle_runtime.probe'):
            mock=patch(target,side_effect=AssertionError('NO NETWORK / INFERENCE / GPU'));mock.start();self.addCleanup(mock.stop)

    def queued(self):
        return self.native._insert({'software_fixture':False,'prepared_id':'prepared','install_id':'install'})

    def completed(self,run):
        folder=self.native.root/run;folder.mkdir()
        path=folder/'output.wav'
        with wave.open(str(path),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\x01\x00'*2400)
        result={'software_fixture':False,'inference_completed':True,'artifact':'output.wav',
                'artifact_sha256':file_sha(path),'profile':'indic_speak','model_revision':self.install['revision']}
        with self.store.tx() as db:db.execute("UPDATE native_research_runs SET state='RETURNED FOR TECHNICAL REVIEW',result=? WHERE id=?",(encode(result),run))
        return path

    def test_prebound_native_capture_and_current_evidence_checks(self):
        run=self.queued()
        with self.assertRaises(AgentError):self.lab.capture_native(self.trial['id'],run)
        self.lab.bind_native(self.trial['id'],run,'native-one')
        self.assertEqual(trial_context(self.store,'native:'+run)['backend'],'native')
        with self.assertRaises(AgentError):self.lab.bind_native(self.trial['id'],self.queued(),'native-two')
        path=self.completed(run);sample=self.lab.capture_native(self.trial['id'],run)
        self.assertEqual(sample,self.lab.capture_native(self.trial['id'],run))
        self.assertEqual(sample['sha256'],file_sha(path))
        self.assertFalse(self.lab.status(self.trial['id'])['expert_accepted_this_benchmark_only'])
        packet,key=self.lab.blind_packet(self.trial['id'])
        self.assertIn(packet['samples'][0]['id'],key)
        self.assertNotIn('native_research_runs',json.dumps(packet))
        self.stage['context']['source_revisions']=[{'id':'changed','revision':2}]
        with self.assertRaises(AgentError):self.lab.status(self.trial['id'])

    def test_native_fixture_relabel_and_late_binding_are_rejected(self):
        with self.assertRaises(AgentError):self.lab.bind_native(self.trial['id'],self.native.queue_fixture(),'fake')
        run=self.queued();self.completed(run)
        with self.assertRaises(AgentError):self.lab.bind_native(self.trial['id'],run,'late')

    def test_native_artifact_tampering_invalidates_capture(self):
        run=self.queued();self.lab.bind_native(self.trial['id'],run,'native-one')
        path=self.completed(run);self.lab.capture_native(self.trial['id'],run)
        path.write_bytes(b'changed')
        with self.assertRaises(AgentError):self.lab.status(self.trial['id'])

    def test_professional_ui_with_native_controls_never_launches_on_open(self):
        from streamlit.testing.v1 import AppTest
        code=('from types import SimpleNamespace\nfrom redpad_pipeline.agents import AgentStore\n'
              'from redpad_pipeline.agent_engine import Engine\nfrom redpad_pipeline.professional_ui import show_trials\n'
              f's=AgentStore({str(self.store.path)!r})\nshow_trials(SimpleNamespace(store=s,engine=Engine(s)))')
        with patch.object(NativeExecution,'run') as native,patch.object(Engine,'execute') as engine:
            at=AppTest.from_string(code).run()
            self.assertFalse(at.exception);native.assert_not_called();engine.assert_not_called()


if __name__=='__main__':unittest.main()
