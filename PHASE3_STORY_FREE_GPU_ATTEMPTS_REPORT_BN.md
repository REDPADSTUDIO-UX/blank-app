# Story AI — ordered free-GPU execution attempts, ১৪ নভেম্বর ২০২৬

**এই run-এ কোনো free platform থেকে real model inference করা যায়নি। Qwen3.5-27B বা fallback
চালেনি; canary, candidate story, creative-quality measurement বা targeted revision হয়নি।**
চার named platform বাস্তব browser-এ ক্রমানুসারে খোলা হয়েছে। সবগুলো environment network policy-তে
আটকেছে। পঞ্চম ধাপে অন্য already-authorized free runtime inventory করা হয়েছে; কোনো eligible
runtime exposed ছিল না। এটি provider-গুলোর global outage/ব্যক্তিগত quota exhaustion-এর দাবি নয়।

## Repository ও authorization

প্রথমে remote/local যাচাই: `REDPADSTUDIO-UX/blank-app`, existing
`feature/video-music-editing-studio`, clean baseline
`bc33937f071bf66fd38e694a92e55d86c2df7caa`। Commit/push-এর আগে remote HEAD আবার যাচাই করা হয়েছে।
Final verified feature-branch SHA chat-এর সমাপ্তির উত্তরে থাকবে। অন্য branch তৈরি বা `main`
modify/merge/push নয়।

এই নতুন user request free-platform attempts, bounded real Story benchmark ও eligible registered
fallback ব্যবহারের authorization দিয়েছে। আগের prompt-এর generic GPU approval requirement-কে
আবার বাধা হিসেবে দেখানো হয়নি। প্রকৃত বাধা network access ও reachable runtime-এর অনুপস্থিতি।
Exact source/bundle/rights, free allocation ও safe execution verification এখনো প্রয়োজন; এই request
থেকে paid resource, hosted inference API বা নতুন risky license acceptance-এর অনুমতি নেওয়া হয়নি।

## Attempt matrix — requested order অনুসৃত

| ক্রম | Platform | বাস্তব observation | Runtime / canary / story |
|---|---|---|---|
| ১ | Google Colab Free — `https://colab.research.google.com/` | Chromium: “This site can’t be reached”, `ERR_TUNNEL_CONNECTION_FAILED`; shell: HTTP CONNECT proxy `403 Forbidden` | শুরু হয়নি |
| ২ | Kaggle Notebooks Free GPU — `https://www.kaggle.com/code` | একই browser tunnel error ও independent shell CONNECT `403` | শুরু হয়নি |
| ৩ | Lightning AI Free — `https://lightning.ai/` | একই browser tunnel error ও shell CONNECT `403` | শুরু হয়নি |
| ৪ | Hugging Face free GPU/ZeroGPU — `https://huggingface.co/spaces` | একই browser tunnel error ও shell CONNECT `403` | শুরু হয়নি |
| ৫ | অন্য already owner-authorized FREE runtime | Connected tools-এ GPU/notebook execution connector নেই; configured runtime variable/outbound identity নেই; attached host-এ GPU নেই। Existing provider ledger-এর paid RunPod-কে free ধরা হয়নি। | Eligible additional runtime পাওয়া যায়নি; paid signup/deployment নয় |

প্রত্যেক named platform-এর browser navigation ও screenshot সরাসরি দেখা হয়েছে। কোনো একটিতে
বসে থাকা বা একই failing generation বারবার submit করা হয়নি। সাধারণ page access-ই ব্যর্থ হওয়ায়
account login, notebook creation, accelerator choice, actual VRAM এবং personal quota দেখা যায়নি।
সেই অজানা তথ্যগুলো null/not-observed; quota exhausted বা account suspended বলা হয়নি।

Callable Browser extension tool এই session-এ exposed ছিল না। Cloud tab API-র প্রথম চেষ্টা
`Browser Use could not read requirements` দিয়েছিল; native Chromium window-এর মাধ্যমে সফলভাবে
চার URL navigate করে failure screen পর্যবেক্ষণ করা হয়েছে। Browser screenshots conversation-এর
actual tool results-এ আছে। Remote screenshot paths repository filesystem-এ উপলব্ধ ছিল না; তাই
Git-এ screenshot image/hash আছে দাবি করা হয়নি। `platform_attempts.json`-এর browser details
সেই পর্যবেক্ষণের transcription; `http_access_checks.json` সরাসরি shell-generated evidence।

## Network diagnosis

Current environment status: observations current, network mode **restricted**, state **enforced**।
Effective allowlist-এ চার platform-এর কোনোটির hostname নেই। Package-manager/GitHub access আছে;
তা থেকে Colab/Kaggle/HF access আছে ধরে নেওয়া হয়নি। Normal inherited proxy/TLS দিয়েই test হয়েছে।
No proxy bypass, alternate routing, credential extraction, certificate/security downgrade বা
network-policy edit করা হয়নি। No callable `cloud_environment.request_changes` action exposed ছিল।
শুধু relevant policy summary সংরক্ষিত; unrelated private network details/secret values নয়।

একটি model ছোট করলেও এই destination-policy block দূর হয় না। তাই load/generation retry বা
weights download করা resources নষ্ট করত; কোনোটি করা হয়নি।

## Attached host inventory ও alternative-runtime check

`host_inventory.json` existing read-only runtime probe থেকে: zero GPUs, `nvidia-smi` absent
(`FileNotFoundError`), CUDA/VRAM unobserved। এটি Kaggle/Colab session নয়। Container available RAM
query-time প্রায় ৭.৩ GiB; free disk প্রায় ৫৯ GiB। Host/container RAM ও অন্য provider-এর RAM
এক মনে করা হয়নি। Model packages torch/transformers/accelerate/bitsandbytes/safetensors এই
inventory-তে absent। Quota/account/free-tier fields unknown। No GPU allocation/tensor canary।

Current connected tool inventory-তে authorized additional free GPU execution endpoint নেই।
Environment metadata-তে configured outbound cloud identity ও runtime variables শূন্য। পুরোনো
Colab T4/9B test report current live session প্রমাণ করে না; তাই সেই historical success-কে এই run-এর
success হিসেবে গণনা করা হয়নি। Paid RunPod বা অন্য নতুন service পরীক্ষা/activate করা হয়নি।

## Primary ও fallback সিদ্ধান্ত

Existing Story registry অপরিবর্তিত:

| Rank | Candidate | Exact revision | এই run |
|---|---|---|---|
| Primary | `Qwen/Qwen3.5-27B`, `hf_text_nf4` | `fc05daec18b0a78c049392ed2e771dde82bdf654` | Not run |
| Alternative ১ | `google/gemma-3-27b-it`, `hf_text_nf4` | `005ad3404e59d6023443cb575daa05336842228a` | Not run |
| Alternative ২ | `google/gemma-3-12b-it`, `hf_text_nf4` | `96b6f1eccf38110c56df3a15bffe176da04bfd80` | Not run |

Primary-এর ২৪ GiB GPU/৩২ GiB RAM, Gemma27-এর ২৪/৪৮ এবং Gemma12-এর ১৬/২৪ GiB registry values
**planning estimates/gates**, measured minimum নয়। বর্তমান provider GPU/RAM দেখা যায়নি; তাই
এই run-এর evidence দিয়ে primary-কে “সব free GPU-তে অসম্ভব” বা fallback-কে verified fit বলা যায় না।
Gemma alternatives registry-shortlisted; current exact bundle/installation/terms receipt verified
বলা হয়নি। নতুন Gemma terms গ্রহণ করা হয়নি। No random model, silent substitution, hosted API,
paid inference বা historical 9B output relabeling। **কোনো model এই run-এ used হয়নি।**

## Story output, evaluation ও improvement status

| Item | ফল |
|---|---|
| Successful free platform | None from this environment |
| Model load / Bengali canary | Not reached / not attempted |
| Primary Story benchmark | Not started |
| Full generated story artifact | **নেই**; `real_story_output=null` |
| Fifteen-criterion QC on new output | Not performed; no output to inspect |
| Targeted improvement / re-test | Not run |
| Before/after measured improvement | Not measured |
| GPU model/VRAM/runtime telemetry | Not available; no GPU execution |
| Independent human creative review | Pending; no candidate |
| Owner creative acceptance | Not granted for any new output |

Prepared benchmark cases/rubrics বা authored fixtures-কে genuine inference হিসেবে নেওয়া হয়নি।
No fabricated story, scores, expert feedback বা success counter। User-এর successful real-benchmark
conditions পূরণ হয়নি; outcome **ACCESS-BLOCKED / REAL BENCHMARK NOT COMPLETED**।

## Saved evidence ও preservation

`verification/story_gpu_attempts_20261114/`:

- `platform_attempts.json`: ordered browser observations, failures ও fifth-step inventory।
- `http_access_checks.json`: চার actual bounded HTTP checks, error text ও duration।
- `network_policy_summary.json`: current enforced policy এবং relevant host-grant absence।
- `host_inventory.json`: current host resources; GPU/provider/account unknowns আলাদা।
- `model_decisions.json`: exact pinned primary/alternative metadata; কোনোটিই run হয়নি।
- `preservation.json`: baseline-এর ১২টি Story/shared/source/registry artifact byte-identical।
- `resume_checkpoint.json`: current authorization scope, precise blockers, safe next sequence ও budget।

Source code/schema/registry/owner locks/model selection বদলানো হয়নি। আগের ২২টি Story test ও
৫৮-test scoped result আবার চালিয়ে নতুন benchmark evidence তৈরি করা হয়নি। শুধু actual access
checks, evidence JSON consistency, preservation hashes ও diff checks করা হয়েছে। এই commit-এ
নতুন engineering বা creative intelligence improvement দাবি নেই।

## Exact resume action

১. Running environment settings-এ intended Colab/Kaggle/Lightning/Hugging Face domains-এর
network grants দিতে হবে; existing GitHub/package-manager grants রেখে। Tools থেকে সেটি পরিবর্তনের
action নেই। Login/model-download/CDN redirects-এর প্রকৃত hostname দেখা গেলে প্রয়োজনীয় grant
আলাদাভাবে নির্ধারণ করতে হবে; blind unrestricted access/proxy bypass নয়।

২. Fresh connection দিয়ে একই order-এ normal browser/official client retry। তারপর account/session,
free allocation/quota ও actual GPU/RAM/disk যাচাই। Platform interactive login চাইলে বর্তমান
request অনুযায়ী blocked লিখে পরের platform; passwords/tokens chat-এ নয়।

৩. Primary exact approved bundle/rights/adapter সম্ভব হলে primary; অন্যথায় ranked registered
eligible fallback, explicit provenance সহ। Network-policy failure-কে VRAM failure হিসেবে লেখা নয়।
Kernel-isolated safe worker binding ও current source/manifest verification ছাড়া পুরোনো runtime
gate সরানো যাবে না। সেই integration-এর readiness পূর্ব checkpoint-এও unverified ছিল; তা এই
access-only run-এ বদলায়নি।

৪. Existing bounded Story scheme reuse: এক ছোট Bengali canary; technical failure হলে immediate
fix ও সর্বোচ্চ এক retry। Canary pass-এর পরে foundation + তিন act + reflection/treatment—একটি
story-এর পাঁচ section, raw output ও exact receipts রেখে lossless assembly। Per section ≤১৫৩৬
output tokens / ≤৪০৯৬ context / ≤২৪০ seconds; actual tokenizer feasibility আগে verify। Existing
seven-call ceiling failed calls-সহ: first canary pass হলে একটি optional targeted revision-এর slot;
canary retry হলে সেই slot খরচ হয়। No bulk generations/automatic retries।

৫. Actual story থাকলেই fifteen-criterion evidence-grounded QC; independent expert review pending
রাখতে হবে যতক্ষণ প্রকৃত review না আসে। Specific defect ও free budget থাকলেই এক targeted revision।
Raw before/after অক্ষত; manual section fill/repair candidate output নয়।

Existing CPU-only checkpoint command, প্রয়োজনে fresh folder-এ:
`python -m redpad_pipeline.story_quality --output work/story-gpu-resume-new`। এটি inference launcher
নয় এবং ইতিমধ্যে completed preparation পুনরাবৃত্তির কারণ নয়। Current blocker settings/access,
নতুন prompt তৈরি করা নয়।

No paid API/GPU/resource, hosted generation API, deployment/Render mutation, production DB/media
change, YouTube publication, model-weight download বা new risky license acceptance হয়েছে।
শুধু authorized feature branch-এ এই evidence/report commit/push করা হয়েছে।
