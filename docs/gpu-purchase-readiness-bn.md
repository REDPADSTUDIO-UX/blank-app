# REDPAD AI Studio — GPU কেনার প্রস্তুতি

২১ নভেম্বর ২০২৬, ঢাকা। ভিত্তি `c83f917b4306889c34a9b99aad551159bdb13fea`। অনুমোদিত শাখা `feature/video-music-editing-studio`। Story Budget-11 ও ঐতিহাসিক ২০-agent প্রমাণ অপরিবর্তিত।

**ক্রয়ের সিদ্ধান্ত — স্থগিত রাখুন।** বর্তমান CPU প্রমাণে নির্দিষ্ট GPU-তে runtime, VRAM, নিরাপদ isolation অথবা শিল্পমান প্রতিষ্ঠিত হয়নি।

| গেট | ফল |
|---|---|
| PRE-GPU ENGINEERING READY | নির্দিষ্ট CPU workflow-এর প্রমাণ আছে। সম্পূর্ণ engineering sign-off বাকি। |
| GPU PILOT READY | হোস্টে kernel isolation, সঠিক local component bundle, লাইসেন্স এবং install/launch অনুমোদন বাকি। |
| CREATIVE QUALITY VERIFIED | স্বতন্ত্র বাংলা সম্পাদক, শ্রোতা ও চিত্র পর্যালোচকের গ্রহণযোগ্যতা বাকি। |
| PRODUCTION READY | বর্তমান genuine output, স্বাধীন QC ও version-specific মালিক অনুমোদন বাকি। |

## ২১ এজেন্ট

‘Fixture’ অর্থ বর্তমান engineering evidence index-এ অন্তর্ভুক্ত সফটওয়্যার কাজের প্রমাণ। সংশ্লিষ্ট input/output contract, দায়িত্ব, module, model state ও evidence pointer প্রতি এজেন্টের জন্য বর্তমান matrix-এ আছে। Pilot-এ নিচের মানদণ্ড ব্যবহার করুন। [বর্তমান matrix](../verification/agent_implementation_matrix_current.json) · [Director–QC–Owner controls](../tests/test_producer_control.py) · [কাস্ট ও কণ্ঠ](../tests/test_voice_casting_integration.py)

| এজেন্ট | সফটওয়্যার | বর্তমান runtime | genuine সক্ষমতার মূল্যায়ন বাকি | প্রোডাকশন / মালিক |
|---|---|---|---|---|
| Director AI | Fixture | `qwen35_27` চলমান | কাহিনি, দৃশ্যের লক্ষ্য ও অভিনয়ের নোটে উৎসের সঙ্গে মিল; সংশোধনের পর অক্ষত দৃশ্য পরীক্ষা | অনুমোদন বাকি |
| Quality Control AI | Fixture | `qwen35_27` বাধাগ্রস্ত | clean/defect controls-এ ভুল অনুমোদন ও ভুল প্রত্যাখ্যান; প্রমাণহীন দাবিতে abstain | অনুমোদন বাকি |
| Story AI | Fixture | `qwen35_27` বাধাগ্রস্ত | কারণ–ফল, চরিত্র কী জানে, setup/payoff, আবেগের পরিবর্তন ও রসিকতা | অনুমোদন বাকি |
| Script AI | Fixture | `qwen35_27` বাধাগ্রস্ত | কথ্য বাংলাদেশি বাংলা, বক্তা ও উপপাঠ; অনুমোদিত সংলাপ ও দৃশ্যের দৈর্ঘ্য অক্ষত | অনুমোদন বাকি |
| Character AI | Fixture | `qwen35_27` বাধাগ্রস্ত | মনস্তত্ত্ব ও সম্পর্ক; শট জুড়ে চেহারা এবং পরিচয় | অনুমোদন বাকি |
| Art Director AI | Fixture | `flux2_klein4` বাধাগ্রস্ত | বাংলাদেশি পরিবেশ, ব্যবহারের দাগ, আলো ও প্রপের অবস্থান | অনুমোদন বাকি |
| Location AI | Fixture | `flux2_klein4` বাধাগ্রস্ত | ঘরের জ্যামিতি, প্রবেশপথ ও ক্যামেরা বসানোর বাস্তবতা | অনুমোদন বাকি |
| Costume Designer AI | Fixture | `flux2_klein4` বাধাগ্রস্ত | চরিত্রোপযোগী পোশাক, সাজ, চুল এবং দৃশ্যের ক্রম | অনুমোদন বাকি |
| Storyboard AI | Fixture | `flux2_klein4` বাধাগ্রস্ত | ক্রিয়া ও প্রতিক্রিয়ার কভারেজ, স্ক্রিন দিক ও শটের উদ্দেশ্য | অনুমোদন বাকি |
| Performance Director AI | Fixture | `qwen35_27` বাধাগ্রস্ত | গতি, দৃষ্টি, বিরতি, শরীরী অভিনয় ও সহ-অভিনেতার প্রতিক্রিয়া | অনুমোদন বাকি |
| Cinematographer AI | Fixture | `qwen35_27` বাধাগ্রস্ত | লেন্স, উচ্চতা, আলো, অক্ষ ও ফ্রেমিংয়ের ধারাবাহিকতা | অনুমোদন বাকি |
| Motion & Physics AI | Fixture | `wan_animate2` বাধাগ্রস্ত | হাত–বস্তুর সংযোগ, ভর, বস্তু স্থায়িত্ব ও সময় | অনুমোদন বাকি |
| Video Generation AI | Fixture | `wan22_5` বাধাগ্রস্ত | ফ্রেম রেট, দৈর্ঘ্য, মুখ, হাত, temporal flicker ও camera drift | অনুমোদন বাকি |
| Voice & Dialogue AI | Fixture | `indic_speak` বাধাগ্রস্ত | উচ্চারণ, স্বর, আবেগ, বক্তা এবং lip-sync; অনুমোদিত reference | অনুমোদন বাকি |
| Continuity Supervisor AI | Fixture | `qwen35_27` বাধাগ্রস্ত | প্রপ, তথ্য, পোশাক ও অক্ষের cross-shot ত্রুটি | অনুমোদন বাকি |
| Music & SFX AI | Fixture | `ace15` বাধাগ্রস্ত | মূল স্কোরের সংযম, রুম টোন, cue timing ও সংলাপের স্পষ্টতা | অনুমোদন বাকি |
| Editing & VFX AI | Fixture | `qwen35_27` বাধাগ্রস্ত | কাটের উদ্দেশ্য, subtitle, measured sync, mix এবং codec | অনুমোদন বাকি |
| Production Manager AI | Fixture | `qwen36_27` বাধাগ্রস্ত | কাজের নির্ভরতা, সঠিক বাধা, ব্যয় ও পুনরুদ্ধারের রেকর্ড | অনুমোদন বাকি |
| Growth AI | Fixture | `qwen35_27` বাধাগ্রস্ত | কাহিনির সঙ্গে সৎ metadata, দর্শক উপযোগিতা ও অধিকার | অনুমোদন বাকি |
| YouTube AI | Fixture | `qwen35_9` বাধাগ্রস্ত | read-only release packet, অধিকার ও মালিকের অনুমতির প্রমাণ | অনুমোদন বাকি |
| Casting Director AI | Fixture | `qwen35_27` বাধাগ্রস্ত | দুই চরিত্রের chemistry ও মুখ/কণ্ঠের সম্মতি এবং পরিচয় | অনুমোদন বাকি |

## হার্ডওয়্যার ও pinned মডেল

RAM/VRAM কলাম registry-র অমাপা পরিকল্পনা সীমা, ক্রয়ের specification নয়। GB কেবল তালিকাভুক্ত weights ও auxiliary files-এর হিসাব। Download staging, duplicate cache, scratch video, audio, source, backup ও output-এর জন্য অতিরিক্ত স্থান লাগে। ২৪ GiB VRAM / ৬৪ GiB RAM / ২০০ GiB ফাঁকা SSD আগে আলোচিত আনুমানিক ধাপভিত্তিক ধারণা। সেই workstation-এ পুরনো ও নতুন সব bundle একসঙ্গে বসানোর প্রমাণ নেই। [Registry ও component hashes](../assets/professional/phase3_candidates.json) · [পুরনো বিকল্প ও মাপের উৎস](../assets/professional/models.json)

| Profile ও pin | আনুমানিক VRAM / RAM GiB | তালিকাভুক্ত GB | Adapter / license metadata |
|---|---:|---:|---|
| `qwen35_27` · `fc05daec18b0a78c049392ed2e771dde82bdf654` | 24 / 32 | 55.59 | `hf_text_nf4` · apache-2.0 |
| `qwen35_moe` · `59d61f3ce65a6d9863b86d2e96597125219dc754` | 32 / 64 | 71.90 | `contract_only` · apache-2.0 |
| `qwen36_27` · `8f33b98937c6031bb49e713dee3e8e185aafd26f` | 24 / 32 | 55.59 | `hf_text_nf4` · apache-2.0 |
| `qwen35_9` · `c202236235762e1c871ad0ccb60c8ee5ba337b9a` | 12 / 16 | 19.33 | `hf_text_nf4` · apache-2.0 |
| `gemma3_27` · `005ad3404e59d6023443cb575daa05336842228a` | 24 / 48 | 54.90 | `hf_text_nf4` · gemma |
| `gemma3_12` · `96b6f1eccf38110c56df3a15bffe176da04bfd80` | 16 / 24 | 24.41 | `hf_text_nf4` · gemma |
| `flux2_klein4` · `e7b7dc27f91deacad38e78976d1f2b499d76a294` | 16 / 24 | 15.98 | `flux2_klein` · apache-2.0 |
| `z_image_turbo` · `f332072aa78be7aecdf3ee76d5c247082da564a6` | 24 / 48 | 32.85 | `z_image` · apache-2.0 |
| `wan_animate2` · `6e8f1973bf0abc2aafd517992e8b6d88c3c46e69` | 80 / 128 | 32.79 | `contract_only` · apache-2.0 |
| `wan_animate2_distilled` · `59e4141466bcb1bf9733eca1bc78be6891c9fbdf` | 64 / 96 | 45.92 | `contract_only` · apache-2.0 |
| `wan22_5` · `b8fff7315c768468a5333511427288870b2e9635` | 24 / 64 | 34.18 | `existing_wan_adapter` · apache-2.0 |
| `ltx25` · `49b093a39c19169a8a81721dcc541e07e945232f` | 80 / 128 | 70.12 | `contract_only` · other |
| `svd_xt` · `9e43909513c6714f1bc78bcb44d96e733cd242aa` | 12 / 32 | 4.51 | `existing_svd_adapter` · other |
| `indic_speak` · `76e0814f189321efe550011850cd288dae366aad` | 12 / 24 | 7.07 | `contract_only` · other |
| `indicf5` · `fb652a96e508091045890dae5bb99fe511facbcf` | 8 / 16 | 1.40 | `contract_only` · mit |
| `indic_parler` · `660bc53c64ae83150613264111708a0465211237` | 8 / 16 | 3.75 | `existing_parler_adapter` · apache-2.0 |
| `ace15` · `19671f406d603126926c1b7e2adc169acbcade22` | 8 / 24 | 10.03 | `contract_only` · mit |
| `stable_audio_small` · `ea2772170fc06f80dfd02bea6e57a44d9d4bc9d3` | 8 / 16 | 1.68 | `existing_sfx_adapter` · other |

| পরিবেশ বা workflow | শ্রেণি | ভিত্তি |
|---|---|---|
| CPU-তে dependency, queue, source/QC ও codec fixture | SUPPORTED BY EVIDENCE | নিয়ন্ত্রিত test ও আগের codec receipt |
| আলাদা ধাপে model load/run/unload | LIKELY | resource lease আছে, বাস্তব GPU-তে memory release মাপা বাকি |
| ২৪ GiB-তে Qwen NF4, FLUX 4B, Wan 5B অথবা speech/music | UNVERIFIED | সঠিক driver, runtime, activation, auxiliary ও decode peak মাপা হয়নি |
| ২৪ GiB-তে Animate ও LTX 2.5-এর বর্তমান planning gate | INCOMPATIBLE | registry gate ৬৪–৮০ GiB; অনুমোদিত কম-মেমরি route-এর মাপ নেই |
| এই execution host-এ native isolation | INCOMPATIBLE | Bubblewrap uid map read-only; অনুমোদিত worker launch-এর prerequisite ব্যর্থ |

Gemma terms ও gated access, FLUX 4B-এর exact variant access, LTX community eligibility এবং SVD/Stable Audio commercial conditions আলাদা করে যাচাই করুন। Indic-Speak-এর Indic Open Model License এবং Llama/SNAC/Vocos, IndicF5-এর custom code ও speaker/reference rights, ACE 1.5-এর aux model ও generated-output terms বাকি। Wan base/distilled component বা LTX Comfy/NVFP4 files পরস্পর বিনিময়যোগ্য ধরে চালাবেন না। দৃশ্য পর্যালোচনার Qwen2.5-VL এবং পুরনো speech/SFX model-গুলোর পৃথক bundle ও runtime-ও যাচাই প্রয়োজন। [Native source lock](../assets/professional/phase3_native_source_lock.json) · [Voice lock](../assets/professional/phase3_voice_selected_source_lock.json) · [GPU handoff](../verification/pre_gpu/gpu_human_handoff.json)

মালিক অনুমোদন দিলে বিচ্ছিন্ন pilot host-এ OS/driver/CUDA/PyTorch, Python, FFmpeg ও model dependency versions লিখুন। Exact revision-এর weights, config, tokenizer, codec, VAE, text encoder ও motion preprocessing manifest দিয়ে SHA-256 মেলান। Installation ও launch অনুমোদন পৃথক রাখুন। স্থির network namespace ও filesystem boundary পরীক্ষা করুন। Kernel probe-এর পরে fake process দিয়ে timeout, child cleanup ও restart চালান। তারপর এক model করে cold load, shortest valid canary, target shot, timeout এবং unload মাপুন। Peak GPU allocated/reserved, host RSS, disk high-water mark, elapsed time ও মুক্ত VRAM লিখুন। CPU offload-এর জন্য PCIe transfer, host RAM ও latency আলাদাভাবে মাপুন। মডেল reuse-এর সময় exact checkpoint/settings pin রাখুন। একই সঙ্গে একাধিক model-এর VRAM fit ধরে নেবেন না। প্রতিটি sample-এ original output, source hashes, device, precision, settings ও logs রাখুন।

## Story, Script, Director ও স্বাধীন QC

Budget-11-এর ৯ call, Foundation ও Act 1-এর structural acceptance, Act 2-এর ৭ structural defect, এবং অসমাপ্ত Act 3 ও Reflection সংরক্ষিত। এই checkpoint-এ কোনো call reserve বা budget বৃদ্ধি হয়নি। আগে একই brief, চরিত্রের জ্ঞান ও অবস্থা, সময়সীমা, variant ও token cap দিয়ে অনুমোদিত writing candidates তুলনা করুন। Original samples অক্ষত রেখে model-অন্ধ reviewer-কে কারণ–ফল, আঞ্চলিক ভাষা, সংলাপের উপপাঠ, রসবোধ ও আবেগের মোড় আলাদাভাবে বিচার করতে দিন। Director-এর critique-এ exact quote বা timecode চাই; seeded clean/defect control দিয়ে QC calibration মাপুন। পরবর্তী revision শুধু অনুমোদিত scene/beat পরিবর্তন করবে। Source hash বদলালে downstream approvals আবার পরীক্ষা করুন। [Budget-11 ফল](../PHASE3_STORY_BUDGET11_ACTUAL_RESULTS_REPORT_BN.md) · [Act 2 recovery](../PHASE3_STORY_ACT2_NO_INFERENCE_RECOVERY_REPORT_BN.md) · [Comparison inputs](../assets/pre_gpu/writing_cases.json)

## ভবিষ্যতের একটি বাস্তব পাইলট — ‘ভেজা রসিদ’

বর্ষার সন্ধ্যা, নারায়ণগঞ্জের ছোট সেলাইয়ের দোকান। মালিক রূপা দেখতে পান সহকারী জামাল ভেজা রসিদটা শুকোতে দিয়েছে। তাতে রূপার মায়ের ওষুধের টাকা লেখা। রূপা ভেবেছিলেন জামাল অগ্রিম নিয়ে গেছে। দৃশ্যের উদ্দেশ্য হলো ভুল বোঝার পর রূপার ক্ষমা চাওয়াকে আচরণে প্রকাশ করা। দুজনই কাল্পনিক প্রাপ্তবয়স্ক চরিত্র। রূপার নীল চাদর ও ডান হাতে রুপার আংটি, জামালের ধূসর শার্ট ও বাঁ হাতের সাদা সেলাই cast lock-এ রাখুন। কাল্পনিক, অধিকার-পরিষ্কার স্বর/ছবি অথবা সম্মত শিল্পীর অনুমোদিত reference ব্যবহার করুন। রূপা শুরুতে হিসাব চান, পরে চায়ের কাপটা জামালের দিকে ঠেলে দেন। জামাল আত্মপক্ষ সমর্থন না করে রসিদ খুলে দেখান।

| শট | শট পরিকল্পনা | সংলাপ ও শব্দ |
|---|---|---|
| A | দোকানের দরজা ও টেবিলসহ ৩৫ mm medium wide; রূপা বামে, জামাল ডানে | রূপা “দোকানের টাকা থেকে নিয়েছ?” বৃষ্টি ও সেলাই মেশিন থেমে যাওয়ার শব্দ |
| B | ৫০ mm medium, একই অক্ষ; জামাল রসিদ খুলে টেবিলে রাখেন | জামাল “না আপা। খালার ওষুধটা বাকিতে দিচ্ছিল না।” কাগজের ঘর্ষণ |
| C | ৮৫ mm insert; রসিদের ভেজা কোণ, কাপের হাতল ও আংটির অবস্থান স্থির | রূপা “আগে বললে না কেন?” জামাল “আপনি হিসাব করছিলেন।” |
| D | ৫০ mm static reaction; রূপা কাপ সরিয়ে জামালের দিকে তাকান | রূপা “চা ঠান্ডা হইছে। গরম করে দিই?” বিরতির পরে সংযত instrumental cue |

Director-এর approved scene থেকে existing Casting lock, Storyboard ও ProductionOps shot/voice packet তৈরি করুন। লক্ষ্য প্রায় ২০–৩০ সেকেন্ড। নির্বাচিত video adapter-এর native resolution/grid/fps অনুযায়ী approved source image থেকে ছোট পৃথক clip, প্রয়োজনে Director-approved splits। Unsupported identity/acting conditioning, retiming বা implicit model fallback অনুমোদনের জায়গায় নেবেন না। Dialogue-এর spoken duration মেপে voice packet-এ ফেলুন। Source transcript ও synthesis text দুটিই রাখুন। রুম টোন, বৃষ্টি, কাগজ ও instrumental আলাদা stems-এ রাখুন। Approved EDL দিয়ে hard cut, subtitle ও dialogue-window ducking; sync ও media duration decode করে মাপুন।

প্রতি বিভাগে মূল model artifact, exact request, revision hash ও technical receipt দিন। Writing-এ পুরো scene এবং revision pair; design/casting-এ reference ও শটের তুলনা; voice-এ dry line ও sync timecode; video-তে native clips; music/SFX-এ stems; editing-এ EDL, export ও timing receipt। স্বাধীন review packet-এ observation, প্রমাণের quote/timecode, failure class এবং revision scope থাকবে। গুরুতর পরিচয়, সম্মতি, ধারাবাহিকতা, sync, আবেগ বা ভাষার ত্রুটি হলে QC ফেরত দেবে। কাট/সংলাপ বদলানোর পর affected sample পুরনোটির সঙ্গে অন্ধ তুলনা করুন। Technical acceptance, স্বাধীন artistic acceptance ও মালিকের version-specific অনুমোদন সব পাওয়ার পর release সিদ্ধান্ত নেওয়া যাবে।

## পরিবর্তন ও দ্বিতীয় audit

Native lifecycle-এ cancellation একই database update-এ state-এর সঙ্গে বাঁধা। Stale queued launch terminal receipt overwrite করতে পারে না। শেষ write-এর আগে cancel commit হলে success receipt প্রকাশ পায় না। Recovery terminal run পুনরায় চালায় না। পুরনো queued request-এ controller digest বদলালে বর্তমান source-pin gate সেটিকে stale করবে; নতুন করে explicit queue/launch প্রয়োজন। শেষ audit-এ state compare-and-set, terminal ফল সংরক্ষণ, no-auto-retry ও fixture-only subprocess পরীক্ষা করা হয়েছে। [Native controller](../redpad_pipeline/native_execution.py) · [Regression cases](../tests/test_native_local_execution.py)

এই পরিবর্তনের পরে CPU regression ৭৩৪টি pass। প্রথম run-এ স্থানীয় virtualenv-এর dependency অনুপস্থিত ছিল, যেমন `cryptography`; বিদ্যমান `requirements.txt` install করার পর regression pass করে। এরপর একই authored fixture project-এ casting/recast, ব্যর্থ worker, restart, duplicate queue প্রতিরোধ, QC rejection, targeted revision ও simulated owner approval একসঙ্গে চালিয়ে পরিবর্তিত test pass করেছে। এই workflow-তে বাংলার original fixture ও codec প্রমাণ ব্যবহার হয়েছে। Consent, technical audio/video timing ও publishing denial-এর পরীক্ষাগুলো regression suite-এ আছে। নতুন real-model call বা human review হয়নি।

বাকি CPU scope-এর মধ্যে native root-এর host-file visibility নিয়ে minimal read-only mount audit রয়েছে। বর্তমান native worker read-only root bind করে; data visibility সীমার জন্য allowlisted mount profile এবং তার host-level test দরকার। বর্তমান host-এর Bubblewrap probe `bwrap: setting up uid map: Read-only file system` দিয়ে ব্যর্থ হয়েছে। বাস্তব driver/kernel, load/unload, leak, timing, identity, performance এবং artistic review উপরের পরবর্তী যাচাইয়ের অংশ। কোনো শতাংশ নির্ধারণ করা হয়নি।
