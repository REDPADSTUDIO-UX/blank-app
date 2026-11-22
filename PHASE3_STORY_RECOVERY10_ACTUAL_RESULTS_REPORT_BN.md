# Story AI Budget-10 — প্রকৃত recovery ফল ও resumable checkpoint

Recovery inference: ২০ নভেম্বর ২০২৬। Saved evidence recovery ও current-VM recheck: ২১ নভেম্বর ২০২৬, Asia/Dhaka। Authorized branch `feature/video-music-editing-studio`।

**Bundle restore ও Foundation v2 technical: VERIFIED COMPLETE। Act1 v2: FAILED HANDOFF VALIDATION। Complete Story benchmark: BLOCKED।**

## Checkpoint correction

Requested old checkpoint `d9ab67c72d050e09a4f05d78071ee58cd3c59476`-এর পরে remote HEAD `da3fa36419196301dc43ece5bb12b17a107cd992` পাওয়া গেছে—এতে Foundation v2 সংরক্ষিত, অর্থাৎ remote evidence-তেই অন্তত ছয় call। Interrupted work session-এর local raw export এবং saved notebook Cell41 আরও একটি genuine Act1 v2 call নিশ্চিত করে। সেই অসম্পূর্ণ evidence checkpoint এখন সংরক্ষণ করা হয়েছে; কোনো generation পুনরাবৃত্তি হয়নি।

**Canonical actual count: historical৫ + recovery২ = ৭/১০ consumed; বাকি৩।** এই ২১ নভেম্বরের resume-এ নতুন inference০। Old metadata cell-এর static3/8 label budget authority নয়। Historical failed calls, initial canaries ও original Foundation/Act1 অপরিবর্তিত।

## Actual hardware, approved restore ও integrity

২০ নভেম্বর বর্তমান VM-এর জন্য owner-এর explicit authorization অনুযায়ী কেবল তিনটি missing artifact restore হয়েছিল। Tesla T4 total15360MiB/free14913MiB; hostRAM13605818368bytes, available12087529472bytes; disk free120839204864bytes। Full artifact sizes/checksums PASS before extraction/execution:

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Qwen3.5-9B-Q4_K_M.gguf | 5680522464 | 03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8 |
| cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 594371580 | caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea |
| llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 197999267 | e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797 |

Pinned model `unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`। Official runtime b12318/7021f7e09; extracted serverSHA256 `0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5` PASS। Actual CUDA backend `ldd` resolved `/usr/lib64-nvidia/libcuda.so.1`; historical driver binding/canary reused, no new canary/enumeration benchmark।

**২১ নভেম্বর fresh observation:** T4 connected,15360MiB total/14913MiB free; RAM13605810176bytes total/12244893696bytes available। কিন্তু exact GGUF local/snapshot paths, server, archives ও receipts সব absent। Current checksums তাই NOT POSSIBLE। Quota/session lifetime অজানা। No reconnect or download this resume। Bundle restore alone cannot override the failed mandatory Act1 stop, তাই অপ্রয়োজনীয় restore করা হয়নি। Exact paths current status JSON-এ আছে।

## Genuine section results

| Section | Actual outcome | Prompt/output tokens | Total/load/generation seconds |
|---|---|---|---|
| Foundation v2 | finish=stop; original schema + existing handoff PASS |1481/815|163.32 /65.14 /94.98|
| Act1 v2 | finish=stop; schema PASS; handoff FAIL,11 findings |2221/1015|42.64 /4.10 /38.25|
| Act2 | NOT RUN — failed predecessor |—|—|
| Act3 | NOT RUN |—|—|
| Reflection/Treatment | NOT RUN |—|—|

Both33/33 layers offloaded। Sampled whole-device usage5249MiB/Foundation ও5253MiB/Act1; serverRSS1613574144bytes ও1466462208bytes। Sampling includes baseline, allocator peak নয়। Both owned servers stopped; postflight GPU process list empty। 4096context,1536output,240sec generation limits unchanged। No truncated prose repaired, no model retry, no dependent section skipped。

Foundation rawSHA256 `a69692f0183fd82623bec718176898e7c85f04529b0bc0fc586de17c09776612`। Act1 rawSHA256 `e975ff24d4afae82b1cba263c82d6c429db9160d9189d19c44f28ac63ba78814`। Raw HTTP/content/hash equality, reserved payload hashes ও original schemas verified; model response path exact approved GGUF।

## Original versus recovery — narrow evidence only

- Foundation IDs N-01/H-01 → exact N/H। N-এর initial knowledge থেকে ticket purchase/hiding বাদ; H-তে TICKET_HIDDEN আছে। এটি নির্দিষ্ট symbolic knowledge-lock improvement, professional story acceptance নয়।
- Act1 beat IDs B1-act_1 ইত্যাদি → B1–B4; actor নাম → N/H। Generic knowledge map key আর নেই; requires/learns empty। Empty maps cognitive understanding প্রমাণ করে না।
- একই unchanged guard-এ combined original26 findings → recovery11। Findings কমা সীমিত structural compliance; cinematic quality score নয়।
- Act1-এর চার cause field-এ earlier beat IDs-এর বদলে JOB_RAJ/FIXED_BAG/TICKET_HIDDEN/N_STATE। চার beat-এ tracked state keys drop/add; দুটো predecessor chain mismatch। B3 emotion_setups-এ earlier beat-এর বদলে SILENCE_RULE। এই11 findings-এ fail-closed stop।
- Bengali coherence এখনও দুর্বল: Foundation behavior “চোখ উঁচুতে রেখে বাবা দেখে না”; H relationship text-এ অস্পষ্ট “কন্যা এবং কৃত্রিম ত্যাগ নয়”; B1 “দরজার পাশের স্টেশন”/“লোহার কলম”; B2 “টিকিট আঁচল থেকে মুছে যায়”। এগুলো সংশোধন করে output বানানো হয়নি।
- B4-এর humor field-এ “গরমি নিয়ন্ত্রণ” explanation আছে, কিন্তু convincing witty interaction প্রতিষ্ঠিত নয়। N-এর costly agency ও dramatic escalation এখনও শক্তিশালী বলে প্রমাণ নেই। Foundation-এর bus-break assumption supplied brief থেকে verified fact নয়।

এই textual triage assistant-এর preliminary assessment, independent expert review নয়। Full story নেই বলে lossless complete-story assembly, three-act validator ও15-criterion full-story QC **NOT RUN**। কোনো artistic numeric score বা professional winner claim নেই।

## Independent review preparation

`partial_blind_review_bn.md`-এ দুইটি genuine Foundation/Act1 attempt-এর unrewritten samples A/B এবং খালি reviewer instructions। Owner-only unblinding key ও15-criterion blank form আলাদা। **Partial diagnostic packet PREPARED; review NOT PERFORMED।** Full-story human-review packet NOT READY। Human, Producer/Owner acceptance PENDING। Ending/full arc excerpts দিয়ে assess করা যাবে না।

## Narrow runtime binding correction ও preservation

Existing research runner specialize করে শুধু auditable Budget10 prefix/five recovery reservations, unique v2 filenames ও saved prompt addenda প্রয়োগ হয়েছে। Guard, original BUNDLE/schema/rubric, source brief এবং server command unchanged। No production engine/worker redesign। New scoped budget checks passed; old engineering suites rerun হয়নি।

প্রথম Act1 preparation-এ আমার adaptation-এর legacy predecessor filename lookup থেকে FileNotFoundError হয়েছিল, model load/reservation-এর আগেই। এটি model call নয়। Minimal filename correction-এর before/after source/hash ও error receipt retained; নতুন CPU preparation regression actual submitted prompt-এর সঙ্গে মিলে PASS। কোনো historical response relabel হয়নি। Original and corrected source snapshots দুটোই retained।

Evidence: `verification/story_recovery10_20261120/recovery_v2_final_actual.json`, `current_vm_recovery_validation.json`, `recovery_lookup_correction.json`, `recovery_lookup_regression.json`, `recovery_adapter_validation.json`, `resume_20261121_status.json`। Existing notebook **All changes saved** verified।

No paid services/API, new model/license, CPU model fallback, extra canary, Bubblewrap bypass, production worker change, Render/main/DB/media/YouTube modifications। Option C research success never establishes production Secure Worker isolation।

## Exact next action

এই checkpoint থেকে **Foundation v2 আবার চালানো নয়; Act2 দিয়ে failed Act1 skip করা নয়**। Failed Act1-এর targeted recovery/alternative workflow এবং call allocation নিয়ে scoped owner decision দরকার। বর্তমান বাকি৩ call Act2/Act3/Reflection-এর জন্য; Act1-এর আরও call অনুমোদিত নয়। Act1 recovery plus those three sections would require at least one additional call and an explicit revised allocation; success still not guaranteed।

পরবর্তী authorized generation সত্যিই সম্ভব হলে তখন current Free T4/cache যাচাই ও applicable owner authorization অনুযায়ী শুধু pinned missing bundle restore। বর্তমান authorization generic resume-কে automatic retry বা budget reset হিসেবে নেওয়া হয়নি।
