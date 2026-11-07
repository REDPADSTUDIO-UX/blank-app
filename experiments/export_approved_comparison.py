"""Integrity-check completed real arms and export metadata-blind review material.
No inference, downloads, scores, reviewer identities or creative approval.
"""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from redpad_pipeline.local_ollama_session import ROOT
from redpad_pipeline.model_benchmark import cases, report, blind_comparison, DIMENSIONS
from redpad_pipeline.staged_writing import digest

OUT=ROOT/'verification/approved_comparison'
FOLDERS=[ROOT/'verification/master_studio/qwen_control',OUT/'gemma3',OUT/'qwen3.5',OUT/'qwen3.5-nonthinking']

def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def export():
    summaries=[];all_reports=[]
    for folder in FOLDERS:
        b=report(folder);all_reports.append(b);rows=[]
        for case in cases():
            r=b['records'][case['id']];e=r['evidence']
            assert r['provenance']=='local_inference' and not r['human_review_completed'] and not r['production_approved']
            assert r['request_sha256']==digest(r['request'])
            assert e['raw_sha256']==hashlib.sha256(r['raw'].encode()).hexdigest()
            assert e['model']==b['model'] and e['model_digest']==b['digest']
            assert r['request'].get('think')==b.get('think')
            if r['status']=='validated_stage':
                assert e['inference_completed'] and json.loads(r['raw'])==r['result']
                assert Draft202012Validator(case['schema']).is_valid(r['result'])
            else:assert r['status']=='failed'
            if 'runtime_thinking' in r and 'thinking_sha256' in e:
                assert hashlib.sha256(r['runtime_thinking'].encode()).hexdigest()==e['thinking_sha256']
            p=folder/(case['id']+'-resource.json');resource=json.loads(p.read_text()) if p.exists() else None
            rows.append({'case':case['id'],'status':r['status'],'wall_seconds':e.get('wall_seconds'),'tokens':e.get('eval_count'),
                         'finish_reason':e.get('finish_reason'),'raw_sha256':e['raw_sha256'],'resource':resource})
        summaries.append({'evidence_folder':str(folder.relative_to(ROOT)),'model':b['model'],'digest':b['digest'],
                          'think':b.get('think'),'options':b['options'],'cases':rows,
                          'completed':sum(r['status']=='validated_stage' for r in rows),'calls':len(rows),
                          'wall_seconds':round(sum(r['wall_seconds'] or 0 for r in rows),3),
                          'criticism_accuracy':b['criticism_accuracy'],'selected_roles':[],'human_review_completed':False})
    save('summary.json',{'arms':summaries,'selected_models':dict.fromkeys(['story','script','director','qc']),
                        'human_review_completed':False,'GPU_inference_calls':0,
                        'limitations':['One case per creative category; not statistical or full-episode validation.',
                         'Default and explicit non-thinking are separate arms, with different thinking controls.',
                         'Same seed does not imply equivalent stochastic draws across tokenizers/models.',
                         'Host CPU load was not isolated; regression checks overlapped some default-arm calls.',
                         'Original default Qwen3.5 adapter discarded message.thinking; final content and counters retained, missing traces cannot be reconstructed.',
                         'Critic TP/FP/FN uses strict line/category matching. Qwen3.5 QC mentions the bag/umbrella contradiction under L2/motivation; semantic partial credit is not assessed by this scorer.',
                         'Sum RSS is sampled aggregate RSS with shared-page duplication, not minimum RAM or PSS.']})
    runtime=['# Observed CPU results',
             'Six identical cases per arm. Original baseline reused; eighteen new calls. No human creative acceptance.',
             '| Model / thinking mode | Complete + schema valid | Failed | Total call seconds | Peak sampled aggregate RSS, GiB |',
             '|---|---:|---:|---:|---:|']
    for b in summaries:
        peak=max((c['resource']['peak_sampled_aggregate_rss_bytes'] for c in b['cases'] if c['resource']),default=0)
        mode='runtime default' if b['think'] is None else str(b['think']).lower()
        runtime.append(f"| {b['model']} / {mode} | {b['completed']}/6 | {6-b['completed']}/6 | {b['wall_seconds']:.3f} | {peak/1024**3:.3f} |" if peak else f"| {b['model']} / {mode} | {b['completed']}/6 | {6-b['completed']}/6 | {b['wall_seconds']:.3f} | not sampled |")
    runtime+=['','| Model / mode | Critic task | TP | FP | FN | Precision | Recall |','|---|---|---:|---:|---:|---:|---:|']
    for b in summaries:
        for task in ('criticism','qc'):
            a=b['criticism_accuracy'].get(task)
            label=b['model']+(' / off' if b['think'] is False else ' / default')
            if a:runtime.append(f"| {label} | {task} | {a['true_positive']} | {a['false_positive']} | {a['false_negative']} | {a['precision']} | {a['recall']} |")
            else:runtime.append(f'| {label} | {task} | — | — | — | no completed answer | no completed answer |')
    runtime+=['','Only one seeded defect; strict line/category matches do not validate semantic correctness or editorial remedies. Qwen3.5 QC mentions the contradiction under L2/motivation, which this scorer penalizes; semantic partial credit needs independent review.',
              'Default Qwen3.5 failure is token exhaustion, not a measured timeout. Each failed call generated 1024 tokens with empty final content.',
              'Sampled aggregate RSS double-counts shared pages; it is not a minimum RAM requirement. CPU load was not isolated.',
              '\n## Per-case timings',
              '| Model / mode | Case | Wall seconds | Generated tokens | Finish reason | Status |',
              '|---|---|---:|---:|---|---|']
    for b in summaries:
        for c in b['cases']:runtime.append(f"| {b['model']} / {b['think']} | {c['case']} | {c['wall_seconds']} | {c['tokens']} | {c['finish_reason']} | {c['status']} |")
    (OUT/'RUNTIME_COMPARISON.md').write_text('\n'.join(runtime)+'\n')
    # Stable package until input changes; do not reshuffle an already issued review.
    fingerprint=digest(all_reports);existing=OUT/'blind-package-input-sha256.txt'
    if not existing.exists() or existing.read_text().strip()!=fingerprint:
        package,key=blind_comparison(FOLDERS)
        save('blind-editorial-package.json',package);save('blind-administrator-key.json',key)
        existing.write_text(fingerprint+'\n')
    package=json.loads((OUT/'blind-editorial-package.json').read_text())
    lines=['# বাংলা blind editorial review — pending',
           'স্বাধীন reviewer এখনো অংশ নেননি। স্কোর, winner বা human approval নেই।',
           'প্রতিটি case আলাদাভাবে বিচার করুন। অসম্পূর্ণ উত্তরকে লেখা হিসেবে অনুমোদন দেবেন না।',
           'একই case-এর প্রার্থীদের তুলনা করুন; administrator key reviewer-কে দেবেন না।',
           'এটি model metadata লুকানো package; ছোট নমুনা ও লেখার ধরন পরিচয় ফাঁস করতে পারে।',
           '\n## Original tasks',json.dumps(package['tasks'],ensure_ascii=False,indent=2),
           '\n## Anonymous unchanged outputs']
    for c in package['candidates']:
        lines.extend(['\n### '+str(c.get('id',c.get('code','candidate'))),
                      '```json',json.dumps(c,ensure_ascii=False,indent=2),'```'])
    lines.extend(['\n## Reviewer worksheet','Reviewer: __________  Independent: __________  Date: __________',
                  'প্রতি candidate/case: score 0–10 অথবা insufficient evidence; exact excerpt; finding; accept/reject/defer।',
                  '\n'+'\n'.join('- '+d+': __________' for d in DIMENSIONS),
                  '\nএই package তৈরি হওয়া review সম্পন্ন হওয়ার প্রমাণ নয়।'])
    (OUT/'BLIND_REVIEW.md').write_text('\n\n'.join(lines)+'\n')
    print(json.dumps([{k:b[k] for k in ('model','think','completed','calls','wall_seconds','criticism_accuracy')} for b in summaries],ensure_ascii=False))

if __name__=='__main__':export()
