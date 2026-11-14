"""Read-only postprocessing of genuine preserved inference, never prose repair."""
import base64,hashlib,html,json,re
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent;EXPORT=HERE/'colab_export'
spec=json.loads((ROOT/'assets/filmmaking/story_benchmark.json').read_text())
contracts=json.loads((ROOT/'verification/story_intelligence/section_contracts.json').read_text())
brief=json.loads((ROOT/'verification/story_intelligence/resume_request.json').read_text())['brief']
rows=[]
for path in sorted((EXPORT/'outputs').glob('*.json')):
 r=json.loads(path.read_text());content=r['raw_content']
 assert hashlib.sha256(content.encode()).hexdigest()==r['raw_content_sha256']
 assert path.with_suffix('.raw.txt').read_bytes()==content.encode()
 http=json.loads(base64.b64decode(r['raw_http_base64']))
 assert http==r['response'] and http['choices'][0]['message']['content']==content
 rows.append({'case':r['case']['id'],'state':r['state'],'finish_reason':r['finish_reason'],'usage':r['response']['usage'],'load_seconds':r['load_seconds'],'generation_seconds':r['generation_seconds'],'total_seconds':r['total_seconds'],'sampled_device_used_mib':r['peak_sampled_device_used_mib'],'sampled_server_rss_bytes':r['peak_sampled_server_rss_bytes'],'offload_lines':r['offload_lines'],'template_sha256':r['template_sha256'],'raw_sha256':r['raw_content_sha256'],'server_stopped':r['server_stopped'],'timings':r['response']['timings']})
foundation=json.loads((EXPORT/'outputs/foundation.json').read_text());raw=foundation['raw_content']
try:
 parsed=json.loads(raw)
 schema_errors=[e.message for e in Draft202012Validator(contracts['foundation']).iter_errors(parsed)]
 decode_error=None
except json.JSONDecodeError as e:
 parsed=None;schema_errors=None;decode_error={'type':type(e).__name__,'message':e.msg,'line':e.lineno,'column':e.colno,'position':e.pos}

quotes={
 'direction':'বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।',
 'awareness_a':'নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।',
 'awareness_b':'নীরা বাবার একাকীত্বের বিষয়টি বুঝতে পারেন না।',
 'unsupported':'ঢাকার ভাড়া বাসা ছেড়ে রাজশাহীতে চাকরির সুযোগ খুব কম।',
 'interview':'নীরা চাকরির ইন্টারভিউয়ের জন্য প্রস্তুত।',
}
evidence={k:{'quote':v,'source':'colab_export/outputs/foundation.raw.txt','occurrences':raw.count(v),'first_character_offset':raw.find(v),'source_sha256':foundation['raw_content_sha256']} for k,v in quotes.items()}
assert all(x['occurrences']>0 for x in evidence.values())

notes=[
 ('পূর্ণ premise বা beat নেই; originality বিচার করা যাচ্ছে না।',[]),
 ('Causal beats ও consequence chain তৈরি হয়নি; canary-র generic inference পূর্ণ গল্পের causal logic নয়।',[]),
 ('চরিত্রের costly decision অনুপস্থিত; canary-তে সিদ্ধান্তের বদলে কী করবে না তার নির্দেশসদৃশ ভাষা এসেছে।',[]),
 ('একাকীত্ব লক্ষ্য করা ও না-বোঝার দাবি পরস্পর অস্পষ্ট; পূর্ণ character motivations নেই।',['awareness_a','awareness_b']),
 ('সম্পর্কের কোনো enacted progression পাওয়া যায়নি।',[]),
 ('Earlier investment ও restrained emotional action-এর story evidence নেই।',[]),
 ('কোনো motivated humor scene তৈরি হয়নি।',[]),
 ('চাকরির সুযোগ কম—এ দাবির source নেই; এটি verified বাংলাদেশি factual context নয়।',['unsupported']),
 ('একটি assumptions list এসেছে; hook বা suspense narrative বিচার করা যাচ্ছে না।',[]),
 ('একই assumptions বারবার এসেছে; escalating choices হয়নি।',['direction','awareness_a']),
 ('Ticket brief-এ আছে; কোনো generated plant-to-payoff story নেই।',[]),
 ('Ending তৈরি হয়নি; ending score দেওয়া যাবে না।',[]),
 ('পশ্চিমের প্রবেশদ্বারকে দক্ষিণ করা হয়েছে; spatial continuity ভেঙেছে।',['direction']),
 ('Brief-এর geography বদলেছে এবং চাকরি নিতে যাওয়াকে interview preparation করা হয়েছে; একাকীত্ব জানার অবস্থাও অস্পষ্ট।',['direction','interview','awareness_a','awareness_b']),
 ('পূর্ণ গল্প/দর্শক-পরীক্ষা নেই; engagement বা viewership দাবি করা যাবে না।',[]),
]
rubric=[]
for criterion,(note,keys) in zip(spec['rubric'],notes):
 rubric.append({**criterion,'status':'partial_defect_observed' if keys else 'not_assessable_missing_complete_story','score':None,'assessment':note,'raw_evidence':[evidence[k] for k in keys],'beat_id':None,'reviewer_kind':'assistant textual triage, not independent qualified human','independent_human_review':'pending'})
assert len(rubric)==15
technical={'raw_http_matches_content':True,'raw_hashes_verified':True,'canary_json_schema_valid':True,'canary_knowledge_boundary':'No prior ticket reaction asserted; generic non-action rather than convincing dramatic decision. Narrow format/knowledge check only; creative quality not passed.','foundation_json_decode_error':decode_error,'foundation_schema_errors':schema_errors,'foundation_finish_reason':foundation['finish_reason'],'lossless_assembly':'not possible; foundation truncated, no acts/reflection','full_story_validator':'not run: no complete candidate artifact; do not supply a fixture or repair prose','fifteen_criterion_rubric':rubric,'independent_scored_assessment':'not accepted: no complete artifact/beat citations/human inspection receipts','owner_acceptance':False,'production_ready':False}
(HERE/'evaluation.json').write_text(json.dumps(technical,ensure_ascii=False,indent=2))
(HERE/'call_summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
status={'baseline_commit':'4d93a8c83e32ca17e9611797c10737ab9d76bed5','branch':'feature/video-music-editing-studio','actual_model':'qwen35_9_approved_gguf','qwen35_27_ran':False,'calls_submitted':2,'ceiling':7,'canary':'Bengali JSON complete, GPU offload proven; creative weakness noted','foundation':'failed: repetitive degeneration, 1536 tokens, finish_reason=length, incomplete JSON','complete_story':False,'acts_and_reflection_ran':False,'targeted_revision_ran':False,'remaining_calls_are_not_permission_to_ignore_truncation_stop':True,'stop_source':'assets/filmmaking/story_benchmark.json budget.policy; verification/story_gpu_attempts_20261114/resume_checkpoint.json','pipeline_gate_unchanged':True,'human_review':'pending','all_owned_model_servers_stopped':True,'resume':'Do not rerun these experiment IDs. Preserve raw failure. Diagnose bounded schema-constrained decoding/repetition control and token-feasibility as a separately labelled variant before any new generation. No claim that this would fix creative quality; no license or access approval currently blocking the tested fallback.'}
(HERE/'resume_checkpoint.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))

lines=['# REDPAD Story AI — বাস্তব T4 benchmark ও human-review packet','',
 '**ফল: GPU execution সফল; সম্পূর্ণ গল্প তৈরির benchmark ব্যর্থ।**','',
 '১৪ নভেম্বর ২০২৬। Existing feature checkpoint থেকে আলাদা approved 9B GGUF fallback run। Qwen3.5-27B চালানো হয়নি।','',
 '## কী যাচাই হয়েছে','',
 '- Live Tesla T4: 15,360 MiB মোট, শুরুতে 14,913 MiB ফ্রি। RAM 12.67 GiB; disk প্রায় 112.64 GiB, শুরুতে প্রায় পুরোটাই ফ্রি।',
 '- Free account: subscription নেই, paid compute units 0। Colab-এ শুরুতে সর্বোচ্চ 1h20m, শেষে 1h estimate; এটি guaranteed quota নয়।',
 '- 27B primary-এর 24/32 GiB এবং Gemma27-এর 24/48, Gemma12-এর 16/24 GiB registry planning gate বর্তমান runtime পূরণ করে না। এগুলো measured absolute minimum নয়। Gemma local terms/access receipt নেই; নতুন gated license গ্রহণ হয়নি।',
 '- Existing approved evaluation variant: unsloth/Qwen3.5-9B-GGUF, revision 3885219b6810b007914f3a7950a8d1b469d598a5; Q4_K_M exact 5,680,522,464 bytes ও SHA-256 মিলে গেছে। Apache-2.0 README pinned hash-ও মিলে গেছে।',
 '- Fresh session-এ approved weights/runtime অনুপস্থিত ছিল; একই অনুমোদিত source পুনঃস্থাপন হয়েছে, পুরোনো specialist benchmarks পুনরায় চালানো হয়নি।',
 '- 33/33 layers GPU-তে offload এবং owned GPU process verified। Localhost-only standalone inference; kernel egress isolation দাবি নেই। Production Engine gate/registry পরিবর্তন করা হয়নি।','',
 '## প্রকৃত দুই call','',
 '| Call | Prompt / output tokens | Generation / model load | Sampled GPU used | Finish |',
 '|---|---:|---:|---:|---|']
for r in rows:
 lines.append(f"| {r['case']} | {r['usage']['prompt_tokens']} / {r['usage']['completion_tokens']} | {r['generation_seconds']:.2f}s / {r['load_seconds']:.2f}s | {r['sampled_device_used_mib']} MiB | {r['finish_reason']} |")
lines+=['','GPU used হলো whole-device 1-second sampling, baseline সহ; exact allocator peak নয়। Generation wall time prompt evaluation-ও অন্তর্ভুক্ত করে। Canary-তে প্রথম prompt processing 65.94s; foundation decode প্রায় 21.19 tokens/s। Foundation context fit 1135+1536=2671 ≤4096; সমস্যাটি context overflow নয়।','',
 '## কেন থামানো হয়েছে','',
 'Canary সম্পূর্ণ Bengali JSON দিয়েছে, তবে সিদ্ধান্ত/ফল generic ও নির্দেশসদৃশ। Foundation বারবার assumptions লিখে 1536-token cap ছুঁয়েছে; finish_reason=length; JSON বন্ধ হয়নি। Brief-এ পশ্চিমে প্রবেশদ্বার, generated text-এ দক্ষিণে। চাকরি নিতে যাওয়া বদলে interview preparation-ও এসেছে।','',
 'Existing checkpoint truncation হলে stop করতে বলে। তাই 2/7 call-এর পর acts/reflection/revision চালানো হয়নি; raw output repair, fixture substitution বা অতিরিক্ত token দিয়ে success বানানো হয়নি। Budget বাড়ানো বা নতুন variant run করা হয়নি।','',
 '## ১৫-criterion review','',
 'Existing rubric অপরিবর্তিতভাবে প্রয়োগ করে নিচে evidence triage করা হয়েছে। পূর্ণ artifact/beat IDs নেই বলে existing full-story validator ও independent review acceptance contract পূরণ করা যায়নি। সব numeric score null; AI textual observations qualified human review নয়।','',
 '| Criterion | পর্যবেক্ষণ |','|---|---|']
for r in rubric:lines.append('| '+r['criterion']+' | '+r['assessment']+' |')
lines+=['','## Human reviewer-এর কাজ','',
 'এটি পূর্ণ গল্পের review নয়; truncated model failure-এর inspection package। নিচের original brief, exact raw canary ও raw foundation পড়ুন। evaluation.json-এ exact source hashes/character offsets/quotes ও original 1/3/5 anchors আছে। পূর্ণ গল্প না থাকলে overall grade দেবেন না। প্রতিটি ভবিষ্যৎ score-এর জন্য actual beat ID, exact quotation, named reviewer inspection receipt লাগবে। Owner acceptance এখনো pending।','',
 '## অপরিবর্তিত original brief','',brief,'',
 '## Exact raw canary — অপরিবর্তিত','', '```text',(EXPORT/'outputs/canary.raw.txt').read_text(),'```','',
 '## Exact raw foundation — অসম্পূর্ণ, অপরিবর্তিত','', '```text',raw,'```','',
 '## সংরক্ষণ ও resume','',
 'colab_export/outputs/*.json-এ exact prompts, HTTP response bytes (base64), content hash, token counts ও telemetry আছে। *.raw.txt-এ exact UTF-8 response। Server logs, installation/license README ও preflight evidence সংরক্ষিত। Export archive SHA-256: 61ed9cc9a23a63f4cfb1bf9c1a01014e119f48ddf082d8b942197112097e7d34।','',
 'দুই owned model server বন্ধ হয়েছে; export-time free VRAM আবার 14,913 MiB। Colab session disconnected/deleted করা হয়নি, ফলে temporary weights এখনও আছে; session idle expiry/remaining quota-এর নিশ্চয়তা নেই।','',
 'পরবর্তী কাজ completed engineering rerun নয়: এই নতুন repetitive decoding failure diagnose করা; bounded schema-constrained decoding/repetition-control ও section budget-এর আলাদা variant review করা। Existing Story runtime hard gate অক্ষত। নতুন অনুমোদনের নামে paid service, license bypass বা generic approval চাওয়া প্রয়োজন নেই; এই run-এর বাধা actual model output failure।','',
 'No main change, deployment, restart, paid API/resource, publishing বা production DB/media change। Evidence-only feature commit-এ [skip ci] [skip render] থাকবে; manual workflow/deploy trigger নয়।']
report='\n'.join(lines)+'\n'
(HERE/'REVIEW_BN.md').write_text(report)
# Standalone readable page; all model text is escaped and cannot execute markup.
table=''.join('<tr><td>'+html.escape(r['criterion'])+'</td><td>'+html.escape(r['assessment'])+'</td></tr>' for r in rubric)
page='''<!doctype html><html lang="bn"><meta charset="utf-8"><title>REDPAD Story T4 — Human Review</title><style>body{max-width:1000px;margin:40px auto;padding:0 24px;background:#f5f4ef;color:#20252a;font:17px/1.8 system-ui,sans-serif}header{background:#172c35;color:white;padding:28px;border-radius:14px}.badge{background:#ffd7a5;color:#392400;padding:8px 12px;border-radius:8px}section{background:white;padding:24px;margin:20px 0;border-radius:12px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:10px;text-align:left;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.8 system-ui}summary{cursor:pointer;font-weight:bold}small{color:#505a61}</style><header><h1>REDPAD Story AI · T4 benchmark</h1><span class="badge">GPU verified · Complete story FAILED</span><p>১৪ নভেম্বর ২০২৬ · Approved Qwen3.5-9B Q4 fallback · Human review pending</p></header><section><h2>বাস্তব ফল</h2><p>Canary সম্পূর্ণ। Foundation 1,536-token সীমায় একই assumptions ঘুরিয়ে লিখে truncate হয়েছে। পূর্ণ গল্প, ending, creative acceptance বা production readiness অর্জিত হয়নি।</p><p>T4 15,360 MiB · RAM 12.67 GiB · 33/33 layers offloaded · sampled peak 5,249 MiB · 2/7 calls used · model servers stopped</p><p>Original benchmark, source code ও main অপরিবর্তিত। Free resources only; no deployment or publishing.</p></section>'''
page+='<section><h2>অপরিবর্তিত brief</h2><p>'+html.escape(brief)+'</p></section>'
page+='<section><h2>১৫ criterion: evidence triage, numeric scores নেই</h2><p>পূর্ণ artifact ও beat IDs অনুপস্থিত; qualified human review pending। নিচে AI textual observations, professional grade নয়।</p><table><tr><th>Criterion</th><th>পর্যবেক্ষণ</th></tr>'+table+'</table></section>'
page+='<section><h2>Exact raw canary</h2><pre>'+html.escape((EXPORT/'outputs/canary.raw.txt').read_text())+'</pre></section>'
page+='<section><details open><summary>Exact raw foundation — অসম্পূর্ণ</summary><pre>'+html.escape(raw)+'</pre></details></section>'
page+='<section><h2>Complete report ও provenance</h2><details><summary>পূর্ণ রিপোর্ট</summary><pre>'+html.escape(report)+'</pre></details></section></html>'
(HERE/'REDPAD_Story_T4_Review_BN.html').write_text(page)
print(json.dumps({'calls':len(rows),'complete_story':False,'rubric_rows':len(rubric),'raw_http_and_hashes_verified':True,'owned_servers_remaining':json.loads((EXPORT/'export_status.json').read_text())['owned_servers_remaining'],'report':str(HERE/'REVIEW_BN.md')},ensure_ascii=False))
