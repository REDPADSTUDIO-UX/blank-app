# Story AI — Foundation/Act1 recovery: Budget-10 checkpoint

২০ নভেম্বর ২০২৬, Asia/Dhaka। Base verified remote HEAD: `df0b035d8ed1a760b2f16371f3c5446f4ba62bce`। Branch: `feature/video-music-editing-studio`।

**GPU: VERIFIED AVAILABLE। Inference: BLOCKED_CURRENT_VM_BUNDLE_MISSING। New calls: ০।**

## প্রকৃত runtime observation

Existing signed-in `REDPAD_Stages_1_3_20261115.ipynb` accessible; Free T4 ইতিমধ্যে connected ছিল, disconnect/reconnect করা হয়নি। Current read-only metadata cell-এর fresh output:

- Observed UTC: `2026-11-20T12:22:21.199555+00:00`।
- Tesla T4, total15360MiB / free14913MiB, driver580.82.07।
- Host RAM total13605818368bytes / available12239581184bytes। UI disk0.08GB/112.64GB। Remaining quota/session duration অজানা।
- Model-এর approved local path ও pinned HF snapshot path—দুটিতেই file absent।
- `option_c_approved/runtime/llama-b12318/llama-server`, দুইটি original runtime archive, `bundle_ready.json`, `driver_binding_verified.json`, runtime `call_ledger.json` ও successful-canary receipt—সব absent।
- Drive mount detected: false। কোনো weight read/load/download বা model inference হয়নি।

Expected model: `unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`, `Qwen3.5-9B-Q4_K_M.gguf`; expected SHA256 `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`। Exact files absent থাকায় current SHA256/dependency checks সম্ভব হয়নি। Historical successful receipts অক্ষত; সেগুলোকে current VM verification বলা হয়নি।

Owner-এর previous restore authorization তখনকার existing VM-এর জন্য ছিল। বর্তমান VM-এ পূর্বের সব bundle/evidence অনুপস্থিত; সেই VM-এর continuity নিশ্চিত করা যাচ্ছে না। Current prompt আগের অনুমোদন current VM-এ explicitly applicable হলেই re-download অনুমোদন করে। এই শর্ত নিশ্চিত হয়নি বলে download চালানো হয়নি। নতুন screenshot/handoff-mark capture request timeout করেছে; উপরোক্ত metadata response তার আগেই সফলভাবে পাওয়া ও সংরক্ষণ হয়েছে। Screenshot সংরক্ষিত দাবি নেই।

## Budget: owner authorization সংরক্ষিত

`verification/story_recovery10_20261120/authorized_call_ledger_budget10.json`-এ canonical saved ledger-এর historical দুইটি entry ও পরের তিনটি entry হুবহু রেখে ceiling8→10 এবং scoped recovery authorization যোগ হয়েছে। আগের ceiling-eight amendment-ও retained।

| Item | Count |
|---|---:|
| Historical consumed calls, failures-সহ | ৫ |
| New calls this session | ০ |
| New authorized total ceiling | ১০ |
| Remaining additional calls | ৫ |

Allocation: regenerate Foundation → regenerate Act1 → Act2 → Act3 → Reflection। Unique recovery-v2 attempt IDs recorded; no canary, candidate competition বা extra retries authorized। **এটি Git-side authorization checkpoint; current Colab ledger migration/install হয়নি।** Old metadata cell-এর static 3/8 label current budget authority নয়।

## Actual prior failure analysis ও versioned input corrections

Existing genuine raw Foundation/Act1 ও26 findings পড়া হয়েছে; কোনো output rewrite হয়নি। `versioned_prompt_corrections.json` এবং `prompt_before_after.diff`-এ targeted changes সংরক্ষিত:

1. Foundation N-01/H-01-এর বদলে exact N/H IDs এবং knowledge maps-এ সেই IDs।
2. Supplied room/job/ticket facts-এর explicit symbolic vocabulary; নীরার initial knowledge-এ ticket purchase/hiding নিষিদ্ধ। Historical Foundation-এর premature knowledge ও ticket লুকানোর behavior সংশোধনের instruction।
3. Act1 exact B1–B4, actorN/H, first cause=brief, later cause actual earlier beat ID। Invented father coercion নিষিদ্ধ।
4. Single tracked progress key; next before অবশ্যই previous after-এর exact copy। Old তিনটি state-chain mismatch-এর targeted correction।
5. requires/learns-এ generic knowledge key নয়; actual character IDs এবং explicitly discovered fact IDs। Empty maps অনুমোদিত; unknown character assignment অনুমান করে পূরণ নয়।
6. Earlier plants/payoffs ও earlier beat-based emotion_setups; emotion-name/self/future reference নয়।
7. Motivated restrained humor, clear Bangladeshi Bengali; unsupported farmer/city/travel assumptions ও অস্বাভাবিক দোহা/চামড়ায় আওয়াজ ধরনের phrasing এড়ানো। কোনো generated dialogue বা story beat আগে থেকে বসানো হয়নি।

Original brief, model/revision, schema, rubric এবং4096context /1536output /240sec limits retained। Existing handoff guard/production architecture পুনর্নির্মাণ করা হয়নি। Input revisions প্রস্তুত; **model-এ জমা দেওয়া হয়নি, creative improvement verified নয়**।

## পাঁচ recovery section-এর ফল

| Section | Result | New calls |
|---|---|---:|
| Foundation v2 | NOT RUN — verified cached bundle absent | ০ |
| Act1 v2 | NOT RUN — Foundation v2 unavailable | ০ |
| Act2 v2 | NOT RUN | ০ |
| Act3 v2 | NOT RUN | ০ |
| Reflection v2 | NOT RUN | ০ |

Complete genuine Story: নেই। New schema/guard validation: NOT RUN, কারণ নতুন generated sections নেই। Full-story15-criterion QC NOT RUN; original-versus-revised output comparison সম্ভব নয়। Independent complete-story review packet NOT READY; human/owner acceptance PENDING। আগের premature knowledge, identity, causality, state ও বাংলা-language defects অমীমাংসিত।

## সংরক্ষণ ও exact next action

Protected old outputs, receipts, guard, runner ও historical ledgers বদলানো হয়নি। নতুন ফাইল শুধু staged budget authorization, versioned prompt corrections/diff, fresh blocker evidence, validation receipt ও এই report। GPU/CPU model inference, নতুন downloads, successful canary/CUDA rerun, paid resource, production worker/Render/main/DB/media/YouTube পরিবর্তন সব০।

**প্রয়োজনীয় owner action:** বর্তমান cache-হীন Colab VM-এ একই exact approved GGUF ও original দুই runtime archive restore করার explicit অনুমোদন নিশ্চিত করা। নতুন model/license প্রয়োজন নেই। তারপর কেবল missing artifacts restore ও current integrity checks, immutable five-call history-সহ Budget10 runtime amendment এবং unique recovery-v2 section routing যাচাই করে Foundation v2-এর একবারের call। Foundation fail হলে stop; dependent calls নয়। সফল পুরোনো canary/engineering পুনরাবৃত্তি নয়।
