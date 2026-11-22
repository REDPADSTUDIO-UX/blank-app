"""CPU-only authored controls, never real model or human-review evidence."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from redpad_pipeline import intelligence as q
from redpad_pipeline.agents import AGENTS, AgentError, AgentStore
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.specialists import example


class CompletionTests(unittest.TestCase):
    def test_existing_21_benchmarks_and_sequential_pinned_recipes(self):
        with patch('socket.socket', side_effect=AssertionError('No network')):
            audit=q.benchmark_audit();plan=q.sequential_evaluation_plan()
        self.assertEqual(audit['missing'],[])
        self.assertEqual({r['agent'] for r in audit['agents']},set(AGENTS))
        self.assertFalse(plan['execution_enabled'])
        self.assertEqual(plan['max_concurrent_models'],1)
        rows=[r for batch in plan['batches'] for r in batch['agents']]
        self.assertEqual(len(rows),21)
        self.assertEqual({r['agent'] for r in rows},set(AGENTS))
        self.assertEqual(rows[0]['agent'],'story')
        pins={(r['model'],r['revision']) for r in q.future_queue()}
        self.assertEqual({(b['model'],b['revision']) for b in plan['batches']},pins)
        self.assertEqual(len(plan['batches']),len(pins))
        for row in rows:
            self.assertTrue(row['minimum_unique_outputs'])
            self.assertTrue(row['review_modes'])
            self.assertFalse(row['all_modalities_verified'])
            for worker in row['selected_support_workers']:
                self.assertRegex(worker['revision'],r'^[0-9a-f]{40}$')
        for row in audit['agents']:
            self.assertEqual(row['layers']['model'],'unverified')
            self.assertEqual(row['layers']['creative_review'],'pending')
            self.assertIsNone(row['model_result'])

    def finding(self, source, **changes):
        f=dict(id='original',criterion='story.1',target='s1',medium='text',
               source_sha256=q.digest(source),severity='error',confidence=.8,
               explanation='Authored continuity defect',correction='Change s1 only',
               responsible_agent='story',retest='Check possession chronology',
               evidence=source['s1'],score=None)
        f.update(changes)
        return f

    def assess(self, source, findings):
        receipt=dict(reviewer='independent fixture reviewer',source_sha256=q.digest(source),
                     medium='text',target='s1',inspected=True,reference='Authored test control')
        return q.assess('story',source,findings,creator='story',reviewer=receipt['reviewer'],
                        receipts=[receipt],provenance='manually_authored_fixture')

    def test_defect_closure_requires_explicit_supported_same_target_recheck(self):
        old={'s1':'key teleports'};new={'s1':'key is returned'}
        before=self.assess(old,[self.finding(old)])
        good=self.finding(new,id='recheck',resolves=['original'],severity='info')
        after=self.assess(new,[good])
        result=q.re_evaluation(before,after)
        self.assertEqual(result['defects'][0]['status'],'resolved_by_reviewer')
        self.assertFalse(result['professional_acceptance'])
        for changes,state in [({'resolves':[]},'not_re_evaluated'),
                              ({'target':'s2'},'not_re_evaluated'),
                              ({'severity':'error'},'defect_persists'),
                              ({'evidence':'not in source'},'evidence_missing')]:
            assessed=self.assess(new,[dict(good,**changes)])
            self.assertEqual(q.re_evaluation(before,assessed)['defects'][0]['status'],state)
        with self.assertRaises(AgentError):q.re_evaluation(before,before)
        with self.assertRaises(AgentError):self.assess(new,[dict(good,resolves='original')])
        contradictory=self.assess(new,[good,self.finding(new,id='still_bad')])
        self.assertEqual(q.re_evaluation(before,contradictory)['defects'][0]['status'],'defect_persists')

    def test_quote_from_a_different_scene_is_not_evidence_for_target(self):
        source={'s1':'key remains lost','s2':'key is returned'}
        finding=self.finding(source,evidence='key is returned')
        report=self.assess(source,[finding])
        self.assertEqual(report['findings'][0]['status'],'abstain')
        self.assertEqual(report['findings'][0]['defect_class'],'evidence_gap')
        with self.assertRaises(AgentError):self.assess(source,[dict(finding,score=5)])

    def test_engine_benchmark_review_revision_and_recheck_are_persisted(self):
        with tempfile.TemporaryDirectory() as d:
            store=AgentStore(Path(d)/'agent_control.sqlite3');engine=Engine(store)
            run=engine.enqueue('art',example('art'))
            self.assertEqual(engine.execute(run),'Awaiting QC')
            task=engine.runs()[0]['task'];packet=engine.quality_packet(task,1)
            record=packet['source']['records'][0];target=record['id']
            def review(revision,source,**changes):
                finding=dict(id='defect',criterion='art.1',target=target,medium='image',
                    source_sha256=q.digest(source),severity='error',confidence=.8,
                    explanation='Authored wire test, no actual visual review',
                    correction='Change style',responsible_agent='art',retest='Inspect same prop region',
                    evidence='Synthetic region receipt',score=None)
                finding.update(changes)
                receipt=dict(reviewer='independent test fixture',source_sha256=q.digest(source),
                    medium='image',target=target,inspected=True,reference='Synthetic fixture only')
                return engine.record_quality_review(task,revision,[finding],reviewer=receipt['reviewer'],receipts=[receipt])
            first=review(1,packet['source'])
            self.assertEqual(first['findings'][0]['defect_class'],'supported_defect')
            store.review(task,1,'Request revision','Test fixture: style only','owner')
            replacement=dict(record,style='New authored test style')
            revised=engine.enqueue_targeted_revision(task,1,[replacement],[target])
            self.assertEqual(engine.execute(revised),'Awaiting QC')
            source=engine.quality_packet(task,2)['source']
            after=review(2,source,id='recheck',severity='info',resolves=['defect'])
            self.assertEqual(after['re_evaluation']['defects'][0]['status'],'resolved_by_reviewer')
            core={k:v for k,v in after.items() if k not in ('re_evaluation','re_evaluation_history')}
            self.assertEqual(after['re_evaluation']['after_sha256'],q.digest(core))
            self.assertEqual(next(t for t in store.tasks() if t['id']==task)['state'],'Awaiting QC')
            event=next(h for h in store.history() if h['action']=='intelligence_review' and json.loads(h['detail'])['revision']==2)
            self.assertEqual(json.loads(event['detail'])['report']['re_evaluation'],after['re_evaluation'])
            with self.assertRaises(AgentError):engine.quality_packet(task,1)


if __name__=='__main__':unittest.main()
