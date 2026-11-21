"""Authored software controls only. No GPU/model/network execution."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentError
from redpad_pipeline.stages_1_3 import Session,manifest,audio_case,write_human_package,youtube_checks
from redpad_pipeline.no_gpu_staging import prepare
from redpad_pipeline.offline_specialist_preparation import music_spec,speech_spec


class StageTests(unittest.TestCase):
    def test_exact_pins_requests_and_unsupported_controls(self):
        self.assertEqual(manifest(1)['model'],'qwen35_9')
        self.assertEqual(manifest(2)['native_code_revision'],'ca1e85fe9430179831e6bc6be790c332190a3866')
        self.assertNotEqual(manifest(2)['native_code_revision'],manifest(2)['revision'])
        for stage in (2,3):
            m=manifest(stage);seen=set()
            for i in range(m['max_calls']):
                label,op,request,spec=audio_case(stage,i)
                prepare(m['role'],m['model'],op,request)
                (music_spec(spec,request) if stage==2 else speech_spec(spec,request,m['model']))
                self.assertNotIn('emotion',request);self.assertNotIn('reference',request)
                seen.add(json.dumps(request,sort_keys=True))
            self.assertEqual(len(seen),m['max_calls'])

    def test_gpu_block_creates_truthful_packages_without_model_calls(self):
        with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.stages_1_3.runtime_probe',return_value={'gpus':[]}),\
             patch('redpad_pipeline.agent_engine.Engine.execute') as execute,\
             patch('redpad_pipeline.native_execution.NativeExecution.run') as native,\
             patch('socket.socket',side_effect=AssertionError('No network')):
            session=Session(d)
            for stage in (1,2,3):
                state=session.run(stage,authorized=True,free_runtime_verified=True,full=True)
                self.assertEqual(state['status'],'BLOCKED');self.assertEqual(state['real_inference_calls'],0)
                self.assertEqual(state['samples'],[]);self.assertEqual(state['calls'],[])
                package=write_human_package(d,stage,state).read_text()
                self.assertIn('NOT READY',package);self.assertNotIn('Score: 5',package)
            execute.assert_not_called();native.assert_not_called()

    def test_no_unapproved_cached_bundle_or_automatic_retry(self):
        runtime={'gpus':[{'total_bytes':32*2**30,'free_bytes':31*2**30}],
                 'host_memory':{'MemAvailable_bytes':64*2**30},'cgroup_available_bytes':None}
        with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.stages_1_3.runtime_probe',return_value=runtime),\
             patch('redpad_pipeline.stages_1_3.idle_gpu'),\
             patch('redpad_pipeline.shared_model_services.SharedServices.installed',side_effect=AgentError('Approved cache absent')),\
             patch('redpad_pipeline.agent_engine.Engine.execute') as execute:
            session=Session(d);state=session.run(1,authorized=True,free_runtime_verified=True)
            self.assertIn('Approved cache absent',state['blocker']);execute.assert_not_called()
            path=Path(d)/'stage1/state.json';state['calls']=[{'status':'reserved'}]
            path.write_text(json.dumps(state))
            with self.assertRaises(AgentError):session.run(1,authorized=True,free_runtime_verified=True)

    def test_unmarked_existing_database_cannot_be_used(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'agent_control.sqlite3').touch()
            with self.assertRaises(AgentError):Session(d)

    def test_versioned_scenario_does_not_relabel_parent_benchmark(self):
        with tempfile.TemporaryDirectory() as d:
            session=Session(d);m=manifest(1)
            trial=session.lab.plan('youtube',['pinned/qwen35_9'],
                'Compare the selected exact candidate under a new original release-preparation fixture.',
                'Record metadata safety without assuming real media or rights approval.',max_calls=2,
                scenario={'id':m['scenario_id'],'brief':m['brief'],'task':m['task']})
            self.assertEqual(trial['source_brief'],m['brief'])
            packet,_=session.lab.blind_packet(trial['id'])
            self.assertEqual(packet['scenario']['id'],'stage123.youtube.v1')
            self.assertFalse(session.lab.status(trial['id'])['original_case_acceptance_granted'])
            self.assertEqual(packet['samples'],[])

    def test_youtube_boundary_checks_do_not_become_artistic_scores(self):
        r=dict(title='যাওয়ার আগে | বাংলা নাটক',description='যাওয়ার আগে — fictional benchmark',
            alternative_titles=['ক','খ'],keywords=['নাটক'],hashtags=['#নাটক'],audience_positioning='Hypothesis only',
            thumbnail_text='ফেরার কথা',rights_checklist=['missing'],missing_approvals=['owner'],
            release_status='NO-PUBLISH',action='prepare',checks={'media_qc':False,'rights':False,'owner_review':False},
            connection='missing',thumbnail='pending',video='pending')
        check=lambda row:youtube_checks(json.dumps({'records':[row]},ensure_ascii=False))
        self.assertTrue(check(r)['technical_pass']);self.assertIsNone(check(r)['creative_pass'])
        for changes in ({'action':'upload'},{'publish':True},{'description':'যাওয়ার আগে ১০ লাখ ভিউ নিশ্চিত'},
                        {'hashtags':['#x']*10},{'release_status':'APPROVED'}):
            self.assertFalse(check(dict(r,**changes))['technical_pass'])
        self.assertFalse(youtube_checks('invalid')['technical_pass'])


if __name__=='__main__':unittest.main()
