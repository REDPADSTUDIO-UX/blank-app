# Story AI — সীমিত handoff engineering fix

২০ নভেম্বর ২০২৬। Base remote feature HEAD: `7a737fc1af6bb62d61ca31dae11d23c6701f64cc`।
Authorized branch: `feature/video-music-editing-studio`।

**Engineering: VERIFIED COMPLETE for this scoped fix। Story benchmark: BLOCKED_INVALID_PRIOR_OUTPUT।**

## কী সংশোধন হয়েছে

Existing standalone research runner `verification/story_budget8_20261119/sections_only_resume_cell.py`-এ deterministic cross-field validation যোগ হয়েছে। Production worker, Dashboard বা অন্য agents পরিবর্তন হয়নি।

- Prior sections থেকে context তৈরির আগে এবং runtime eligibility/model launch-এর আগে identity/knowledge/state guard চলে।
- Unknown character knowledge key এখন raw `KeyError` না ঘটিয়ে `StoryHandoffError` দেয়; findings-এ exact path, error code ও `repair_applied=false` থাকে।
- Existing prompt-এর exact N/H identities, B1–B12 beat identities, earlier causal references, complete character knowledge mapping, established fact references, before/after continuity, setup/payoff ও earlier emotional references যাচাই হয়।
- নতুন output JSON schema পাস করলেও handoff contract না মানলে `stopped_with_evidence` হয়। Original raw HTTP/text, hashes, finish reason ও consumed call reservation সংরক্ষিত থাকে; section-কে completed বা professionally accepted বলা হয় না।
- কোনো ID alias, inferred speaker, knowledge reassignment, prose rewrite, silent retry বা output repair নেই।

`guard_source.py` reviewable source; exact same definitions runner-এ embedded, যাতে Colab-এ নতুন module download/import dependency না লাগে। Parity test drift আটকায়। এটি নতুন inference engine নয়।

## প্রকৃত CPU যাচাই

**১১টি distinct নতুন handoff test PASS; ২টি affected adapter/budget regression test PASS। মোট ১৩টি distinct test।** Initial mock-fixture corrections-এর repeated runs অতিরিক্ত test হিসেবে গণনা হয়নি।

- Saved genuine Foundation/Act1 output replay: **২৬টি structural finding**, raw input অপরিবর্তিত।
- Existing `generate_section('act_2')` entry point-এ সেই actual output দিলে model dispatch, runtime launch বা ledger mutation-এর আগেই deterministic rejection।
- Valid CPU fixture-তে explicit disclosure ও chronological state progression গ্রহণ; malformed/unknown identity, premature required knowledge, causal/state discontinuity, unsupported reveal ও emotional reference প্রত্যাখ্যান।
- Mocked model transport দিয়ে post-generation failure test: schema PASS হলেও invalid handoff কখনো completed নয়; raw response ও consumed call retained। **Mock transport প্রকৃত inference নয়।**
- Existing eighth/ninth-call boundary regression PASS।
- ৫৮টি পূর্ববর্তী evidence/source file byte-identical। Original BUNDLE, BASELINE, budget functions, section prompt construction, model-server command ও 4096/1536/240 limits অপরিবর্তিত। `git diff --check` PASS।

Evidence: `verification/story_handoff_fix_20261120/cpu_tests.txt`, `affected_budget_tests.txt`, `actual_output_replay.json`, `preservation.json`।

## কী সম্পন্ন হয়নি

এই fix কাহিনির ভুল ঠিক করে না। Foundation-এর premature ticket knowledge, Act1-এর ভুল actor/knowledge keys, state breaks ও অস্বাভাবিক ভাষা আগের মতোই আছে। Symbolic fact validation বাংলা prose-এর অর্থ বা সত্যতা প্রমাণ করে না; independent editorial review এখনও দরকার।

Earlier saved outputs ঐতিহাসিকভাবে JSON/schema-pass; নতুন guard-এর structural handoff acceptance তারা পাস করে না। Historical ledger-এ তাদের পুরোনো status rewrite করা হয়নি; বর্তমান rejection আলাদা CPU replay receipt-এ সংরক্ষিত।

**Model calls: ৫/৮ consumed, বাকি ৩; এই engineering session-এ নতুন call ০।** GPU, CPU model inference, model download, canary/CUDA rerun, paid resource, Render/main/production/YouTube পরিবর্তন সব ০। Updated runner GitHub-এ প্রস্তুত; Colab-এ install/execute বা GPU retest এই session-এ করা হয়নি।

Full story, ১৫-criterion full-story creative QC ও complete-story human-review packet এখনও অসম্পূর্ণ। Human/Owner artistic acceptance PENDING; professional readiness দাবি নেই।

## পরের checkpoint

আর `KeyError` পাশ কাটানোর দরকার নেই—invalid predecessor এখন পরিষ্কারভাবে প্রত্যাখ্যাত হবে। কিন্তু আগের defective output ব্যবহার করে Act2 চালানো নিরাপদ/valid নয়। Owner-কে exact defective sections-এর scoped regeneration/revision এবং তার call-budget সিদ্ধান্ত নিতে হবে। বাকি তিন call শুধু Act2/Act3/Reflection-এর জন্য; Foundation/Act1 পুনরায় generation-এর অনুমোদন বা বাড়তি call এই fix দেয় না। Original responses অপরিবর্তিত রাখতে হবে।

পরবর্তী কাজ শুরুতে নতুন remote feature HEAD পড়তে হবে; successful bundle restore, canary বা পূর্ববর্তী inference অকারণে পুনরাবৃত্তি নয়।
