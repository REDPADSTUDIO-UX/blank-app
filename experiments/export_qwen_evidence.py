"""Summarize only saved genuine model calls. No inference or guessed creative score."""
import hashlib,json,unicodedata
from pathlib import Path
from redpad_pipeline.cpu_creative_trial import FOLDER,MODEL


def export():
    records=[]
    for path in sorted(FOLDER.glob('trial_*.json')):
        row=json.loads(path.read_text());records.append(dict(file=path.name,kind='creative_research',**{k:row.get(k) for k in ('agent','state','error','wall_seconds')},evidence=row['evidence'],raw=row['raw']))
    for name in ('cpu_smoke','control_probe','nfc_control_probe'):
        row=json.loads((FOLDER/(name+'.json')).read_text());records.append(dict(file=name+'.json',kind='control',agent='runtime',state='JSON reply' if row.get('result') is not None else 'Failed',error=row.get('error',''),wall_seconds=row.get('wall_seconds',row.get('seconds')),evidence=row['evidence'],raw=row['raw']))
    engine=json.loads((FOLDER/'engine_roundtrip.json').read_text());runtime=engine['runtime_records'][-1]
    evidence=json.loads(runtime['evidence'])
    records.append(dict(file='engine_roundtrip.json',kind='actual_task_engine',agent='story',state=engine['state'],error=engine['runs'][0]['error'],wall_seconds=evidence.get('wall_seconds'),evidence=evidence,raw=runtime['raw_text']))
    for record in records:
        assert record['evidence'].get('model',MODEL)==MODEL
        if record['raw'] and record['evidence'].get('raw_sha256'):
            assert hashlib.sha256(record['raw'].encode()).hexdigest()==record['evidence']['raw_sha256'],record['file']
    complete=[r for r in records if r['evidence'].get('inference_completed') is True]
    incomplete=[r for r in records if not r['evidence'].get('inference_completed')]
    source=json.loads((FOLDER/'control_probe.json').read_text());fixed=json.loads((FOLDER/'nfc_control_probe.json').read_text())
    matched=[r for r in records if isinstance(r['evidence'].get('eval_count'),int) and r['evidence'].get('eval_duration_ns',0)>0]
    candidates=[json.loads(p.read_text()) for p in FOLDER.glob('trial_*.json')]
    report=dict(model=MODEL,manifest_sha256='0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0',runtime='Ollama 0.40.15',device='CPU',actual_attempts=len(records),completed_runtime_replies=len(complete),incomplete_or_failed_runtime_attempts=len(incomplete),
       accepted_micro_contracts=sum(str(r['state']).startswith('Micro-contract valid') for r in records),completed_but_initial_contract_rejections=[r['file'] for r in complete if r['state']=='Failed'],
       unfinished_reasons=[dict(file=r['file'],reason=r['error'],finish_reason=r['evidence'].get('finish_reason')) for r in incomplete],
       actual_engine_state=engine['state'],engine_echo=True,engine_output_is_new_creative_material=False,
       unicode_control=dict(before_exact=source['checks']['bangla_name_exact_copy'],after_canonical=fixed['checks']['bangla_name_canonical_copy'],arithmetic_unchanged=True,object_transfer_unchanged=True),
       aggregate_decode_tokens_per_second=round(sum(r['evidence']['eval_count'] for r in matched)/(sum(r['evidence']['eval_duration_ns'] for r in matched)/1e9),2),
       total_call_wall_seconds=round(sum(r['wall_seconds'] or 0 for r in records),3),
       peak_sampled_aggregate_rss_bytes=max(r.get('aggregate_process_peak_rss_bytes',0) for r in candidates),
       memory_note='Aggregate sampled RSS of caller and owned server/runner; not unique allocation. The first non-stream timeout supplied no raw text or decode counters.',
       approved_for_production=False,independent_human_review=False,bengali_creative_quality_passed=False,phase3_complete=False,
       actual_visual_assets=0,actual_video_assets=0,actual_speech_assets=0,cinematic_export=None,
       record_manifest=[{k:v for k,v in r.items() if k not in ('raw','evidence')}|dict(raw_sha256=r['evidence'].get('raw_sha256'),completed=r['evidence'].get('inference_completed',False),decode_tokens=r['evidence'].get('eval_count')) for r in records])
    (FOLDER/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    review=dict(reviewer='Codex assistant — model-based editorial inspection, not independent human review',scores=None,owner_approval=False,
       findings=[
        dict(category='Unicode identity preservation',status='specific technical improvement verified',before='control_probe.json',after='nfc_control_probe.json',evidence_before=source['result']['copied_name'],evidence_after=fixed['result']['copied_name'],assessment='Canonical-equivalent input fixed the exact-name copy in one paired controlled test. This does not establish general dramatic quality.'),
        dict(category='Causal story logic',status='not accepted',source='trial_story_nfc.json',quote='রাশেদ অফিসে পৌঁছায় এবং কাজের কাজ শুরু করে।',assessment='Repetitive phrasing and weak causal links remain. Umbrella possession and travel are not made sufficiently clear for the requested relatable family scene.'),
        dict(category='Natural Bengali dialogue and humor',status='not accepted',source='trial_dialogue_nfc.json',quote='হ্যাঁ, আমি আসব না, কারণ আমি বাবার চোখে দেখি না।',assessment='The requested breakfast/paratha situation and affectionate wit are not conveyed; the meaning remains unclear after revision.'),
        dict(category='Scene/location language',status='not accepted',source='trial_script_nfc.json',quote='INT. বাড়ির খাদি ঘর - সকাল',assessment='The requested breakfast-room location is not naturally expressed; other phrases also need editorial rewriting.'),
        dict(category='Music/SFX text plan',status='unverified and weak',source='trial_script_nfc.json',quote='সাদা পানির শব্দ',assessment='This is not a validated musical cue. No audio was generated or listened to; music/acting quality cannot be inferred from this text.'),
        dict(category='Director evidence integrity',status='initial review rejected',source='trial_director_compact.json',quote='রাশেদ তুমি ছাতা দেখে না, আমি তো দেখেছি।',assessment='This quoted string is absent from the actual source. The quote gate rejected the review. Later bounded critic replies were incomplete, not approved QC.'),
        dict(category='Targeted revision scope',status='technical wrapper repaired; artistic improvement not demonstrated',source='script_revision_postcheck.json',assessment='The exact s2 object can be wrapped as one target without altering s1. The revised narrative still contains the observed defects; no production approval follows.'),
        dict(category='Real task-engine generation',status='technical connection verified; generation quality not demonstrated',source='engine_echo_postcheck.json',assessment='The model returned supplied instruction text. The engine now flags canonical input echoes; Awaiting QC is not a creative pass.')])
    for finding in review['findings']:
        if 'quote' in finding:
            row=json.loads((FOLDER/finding['source']).read_text())
            assert finding['quote'] in json.dumps(row,ensure_ascii=False),finding['source']
    (FOLDER/'editorial_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    sample_names=['cpu_smoke','trial_dialogue_revision','trial_dialogue_nfc','trial_story_nfc','trial_script_nfc','trial_director_compact']
    lines=['# Actual Qwen CPU Bengali samples','Original model output, including defects. Experimental only; no owner/independent human approval. No manual rewriting of these samples.']
    for name in sample_names:
        row=json.loads((FOLDER/(name+'.json')).read_text());lines+=['','## '+name,'```json',json.dumps(row.get('result'),ensure_ascii=False,indent=2),'```']
    (FOLDER/'BENGALI_SAMPLES.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ('actual_attempts','completed_runtime_replies','incomplete_or_failed_runtime_attempts','accepted_micro_contracts','aggregate_decode_tokens_per_second','peak_sampled_aggregate_rss_bytes','actual_engine_state')},indent=2))

if __name__=='__main__':export()
