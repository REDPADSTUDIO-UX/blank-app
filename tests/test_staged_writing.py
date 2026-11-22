import copy
import json
from pathlib import Path
import tempfile
import unittest
from jsonschema import Draft202012Validator
from redpad_pipeline.staged_writing import *
from redpad_pipeline.staged_bengali import INITIAL, NAMES, DOMAINS, run_next

class StagedWritingTests(unittest.TestCase):
    def test_schema_requires_action_first_known_speaker_no_extra_fields(self):
        schema=scene_schema(NAMES);v=Draft202012Validator(schema)
        good={'heading':'INT. ঘর','beats':[{'type':'action','text':'ছাতা টেবিলে।'},
             {'type':'dialogue','speaker':NAMES[0],'text':'ছাতাটা নাও।'},
             {'type':'action','text':'সে হাত বাড়ায়।'},
             {'type':'dialogue','speaker':NAMES[1],'text':'তুমি?'}]}
        self.assertTrue(v.is_valid(good))
        for change in ('first','speaker','extra','length'):
            x=copy.deepcopy(good)
            if change=='first':x['beats'][0]=x['beats'][1]
            if change=='speaker':x['beats'][1]['speaker']='অন্য'
            if change=='extra':x['approval']=True
            if change=='length':x['beats'][0]['text']='ক'*181
            self.assertFalse(v.is_valid(x),change)

    def test_state_prevents_remote_transfer_and_travel_with_transfer(self):
        before=dict(INITIAL,umbrella=NAMES[0]);after=dict(before,umbrella=NAMES[1])
        state_check(before,after,NAMES)
        for bad in [dict(after,**{NAMES[1]:'door'}),dict(after,**{NAMES[0]:'office'})]:
            with self.assertRaises(WritingError):state_check(before,bad,NAMES)
        before[NAMES[1]]='door'
        with self.assertRaises(WritingError):state_check(before,after,NAMES)

    def test_director_pins_source_no_authored_quote_no_automatic_edits(self):
        scene={'beats':[{'type':'action','text':'ছাতা টেবিলে।'}]}
        review={'findings':[{'line_id':'L1','criterion':'visual','problem':'অস্পষ্ট','suggestion':'আলো দিন'}]}
        out=ground_review(review,scene,digest(scene));self.assertEqual(out['findings'][0]['evidence'],'ছাতা টেবিলে।')
        self.assertFalse(out['automatic_revision_allowed'])
        for x in [dict(review,quote='মিথ্যা'),{'findings':[dict(review['findings'][0],line_id='L2')]}]:
            with self.assertRaises(WritingError):ground_review(x,scene,digest(scene))
        changed=copy.deepcopy(scene);changed['beats'][0]['text']='বৃষ্টি।'
        with self.assertRaises(WritingError):ground_review(review,changed,digest(scene))

    def test_cache_skips_inference_and_changed_request_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[];lab=StagedDraft(d)
            def fake(*args):calls.append(args);return {'text':'গল্প'}
            args=('a','story',{},'write',obj({'text':text_schema()}))
            r=lab.run(*args,complete=fake);self.assertEqual(r['provenance'],'simulation')
            self.assertFalse(r['human_review_completed']);lab.run(*args,complete=fake)
            self.assertEqual(len(calls),1)
            with self.assertRaises(WritingError):lab.run('a','story',{},'changed',args[-1],complete=fake)

    def test_failed_stage_saved_not_accepted_or_silently_retried(self):
        with tempfile.TemporaryDirectory() as d:
            lab=StagedDraft(d);args=('a','story',{},'write',obj({'text':text_schema()}))
            r=lab.run(*args,complete=lambda *a:{'bad':True});self.assertEqual(r['status'],'failed')
            with self.assertRaises(WritingError):lab.run(*args,complete=lambda *a:{})
            with self.assertRaises(WritingError):lab.run('b','script',{},'write',args[-1],dependencies=['a'],complete=lambda *a:{})
            lab.retry('a');lab.run(*args,complete=lambda *a:{})
            with self.assertRaises(WritingError):lab.retry('a')
            self.assertTrue((Path(d)/'a.attempt-1.json').exists())

    def test_blind_package_unreviewed_no_model_labels_no_scores(self):
        out,mapping=blind_package({'old':{'text':'আগে'},'new':{'text':'পরে'}})
        self.assertEqual(len(mapping),2);self.assertIsNone(out['ratings']);self.assertFalse(out['human_review_completed'])
        for c in out['candidates']:self.assertEqual(c['sha256'],digest(c['text']));self.assertNotIn('model',c)

    def test_pipeline_rejects_duplicate_character_and_invalid_stage_id(self):
        with tempfile.TemporaryDirectory() as d:
            p={'characters':[{'name':NAMES[0],'want':'কাজ','fear':'দেরি','habit':'তাড়া','emotional_change':'মমতা'}]*2,
               'opening_image':'বৃষ্টি','emotional_payoff':'মমতা','ending_decision':'অপেক্ষা'}
            r=run_next(d,complete=lambda *a:p);self.assertEqual(r['status'],'failed')
            with self.assertRaises(WritingError):run_next(d,complete=lambda *a:p)
            with self.assertRaises(WritingError):StagedDraft(d).run('../bad','story',{},'',{},complete=lambda *a:{})

    def test_localwriter_schema_snapshotted_and_invalid_schema_rejected(self):
        schema=obj({'x':text_schema()});w=LocalWriter('qwen:local',format_schema=schema)
        schema['properties']['x']['maxLength']=1
        self.assertEqual(w.format_schema['properties']['x']['maxLength'],180)
        from jsonschema.exceptions import SchemaError
        with self.assertRaises(SchemaError):LocalWriter('qwen:local',format_schema={'type':'invalid'})

    def test_director_cannot_quote_other_scene_or_global_metadata(self):
        from tests.test_creative import samples, request
        from redpad_pipeline.creative import prepare_creative
        from redpad_pipeline.agents import AgentError
        data=samples();source=data['screenplay'];review=data['direction_script']
        review['scenes'][0]['evidence']=source['scenes'][1]['beats'][0]['text']
        with self.assertRaises(AgentError):prepare_creative('director',request('direction',review,source=source))
        review=data['direction_script'];review['revision_notes']=[{'target':'s1','agent':'script','issue':'fixture',
             'evidence':source['title'],'instruction':'fixture'}]
        with self.assertRaises(AgentError):prepare_creative('director',request('direction',review,source=source))

    def test_schema_sent_and_raw_preserved_when_runtime_violates_schema(self):
        from unittest.mock import patch
        from tests.test_cpu_creative import response
        schema=obj({'text':text_schema()});w=LocalWriter('local-test',format_schema=schema)
        with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),response({'model':'local-test','done':True,'message':{'content':'{"extra":true}'}})]) as transport:
            with self.assertRaises(WritingError):w('system','prompt')
            sent=json.loads(transport.call_args.args[0].data)
        self.assertEqual(sent['format'],schema)
        self.assertEqual(w.last_raw_output,'{"extra":true}');self.assertTrue(w.last_evidence['inference_completed'])

    def test_staged_ui_does_not_run_on_open(self):
        from unittest.mock import patch
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.staged_writing_ui.ROOT',Path(d)),patch('redpad_pipeline.staged_writing_ui.run_next') as execute:
            at=AppTest.from_string('from redpad_pipeline.staged_writing_ui import show_staged\nshow_staged()').run()
            self.assertFalse(at.exception);execute.assert_not_called()
            at.text_input(key='staged_id').set_value('../bad').run()
            self.assertFalse(at.exception);self.assertTrue(at.error);execute.assert_not_called()

    def test_fixed_goals_cannot_be_swapped_and_old_bad_plan_is_not_resumed(self):
        from redpad_pipeline.staged_bengali import GOALS
        plan={'characters':[{'name':n,'want':GOALS[n],'fear':'দেরি','habit':'তাড়া','emotional_change':'মমতা'} for n in NAMES],
              'opening_image':'বৃষ্টি','emotional_payoff':'মমতা','ending_decision':'অপেক্ষা'}
        schema=plan_schema(NAMES,GOALS);self.assertTrue(Draft202012Validator(schema).is_valid(plan))
        plan['characters'][0]['want']=GOALS[NAMES[1]]
        self.assertFalse(Draft202012Validator(schema).is_valid(plan))
        with tempfile.TemporaryDirectory() as d:
            # Legacy mechanically valid but semantically inverted plan is preserved,
            # and current workflow must refuse to pass it to the next stage.
            lab=StagedDraft(d);lab.run('plan','story',{},'legacy',plan_schema(NAMES),complete=lambda *a:plan)
            with self.assertRaises(WritingError):run_next(d,complete=lambda *a:{})

    def test_travel_cannot_skip_the_route(self):
        with self.assertRaises(WritingError):state_check(INITIAL,dict(INITIAL,**{NAMES[1]:'interview'}),NAMES)
        state_check(INITIAL,dict(INITIAL,**{NAMES[1]:'door'}),NAMES)

    def test_modified_cached_output_and_dependency_path_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            lab=StagedDraft(d);args=('a','story',{},'write',obj({'text':text_schema()}))
            lab.run(*args,complete=lambda *a:{'text':'মূল'})
            p=Path(d)/'a.json';r=json.loads(p.read_text());r['result']['text']='বদল';p.write_text(json.dumps(r))
            with self.assertRaises(WritingError):lab.run(*args,complete=lambda *a:{})
            with self.assertRaises(WritingError):lab.run('b','story',{},'write',args[-1],dependencies=['../outside'],complete=lambda *a:{})

    def test_fixed_scene_slots_preserve_every_model_text_and_assign_protocol_roles(self):
        r={'heading':'INT. বাসা','opening_action':'টেবিলে ছাতা।','first_reply':'তুমি নাও।','second_reply':'আর তুমি?','closing_action':'সে থামে।'}
        scene=expand_compact_scene(r,NAMES)
        self.assertTrue(Draft202012Validator(scene_schema(NAMES)).is_valid(scene))
        self.assertEqual([b['text'] for b in scene['beats']],[r[k] for k in ('opening_action','first_reply','second_reply','closing_action')])
        self.assertEqual([b['speaker'] for b in scene['beats'] if b['type']=='dialogue'],NAMES)
        with self.assertRaises(WritingError):expand_compact_scene(r,[NAMES[0],NAMES[0]])

    def test_compact_slots_do_not_launder_narrated_or_misattributed_speech(self):
        good={'heading':'INT. বাসা','opening_action':'টেবিলে ছাতা।','first_reply':'তুমি নাও।','second_reply':'আর তুমি?','closing_action':'সে থামে।'}
        for key, text in [('first_reply','তানিয়া বলে, আমি যাব।'),('closing_action',"রাশেদ বলে, 'যাও।'")]:
            r=dict(good);r[key]=text
            with self.assertRaises(WritingError):expand_compact_scene(r,NAMES)
