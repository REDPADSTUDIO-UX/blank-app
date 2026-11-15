# Stages 1–3 — connected Chrome / actual free Colab execution

১৫ নভেম্বর ২০২৬, বাংলাদেশ সময়। **Browser access ও hardware preflight VERIFIED COMPLETE;
তিনটি model stage BLOCKED; genuine model inference ০।**

Remote feature HEAD `9cdca34fb8df48cdcff0ec559ff9ccb960e334dc` যাচাই করে latest
`verification/real_stages_1_3_20261115/STAGES_1_3_CACHED_MODELS_ONLY.ipynb` ব্যবহার হয়েছে।
Notebook নিজেই source code commit `877a475f344d85e19ea45338f3dff8d421a888e5` pin করে;
সেই source-only setup অপরিবর্তিতভাবে existing free Colab-এ চালানো হয়েছে। Pin চুপচাপ বদলানো,
model substitution, dependency installation বা previous engineering পুনরায় করা হয়নি।

## প্রকৃত execution

Chrome extension দিয়ে owner-এর existing authenticated blank Colab notebook claim করা গেছে।
Notebook এখন `REDPAD_Stages_1_3_20261115.ipynb`; final UI-তে **All changes saved** দেখা গেছে।
Source setup, actual hardware/dependency probe, read-only cache/receipt inspection, তিনটি
stage-এর original canary gate এবং evidence export/summary ordinary notebook UI দিয়ে চালানো হয়েছে।
Full-generation cells চালানো হয়নি—canary eligibility-ই pass করেনি।

একটি browser request timeout-এর সময় Colab disconnected ও autosave failed দেখায়। DOM-এ
Stage 1 cell তখনও অনুপস্থিত ছিল; request executed হয়েছে ধরে retry করা হয়নি। Existing
runtime-এর official **Reconnect** একবার সফল হলে তিনটি stage gate একবার করে চালানো হয়েছে।
শেষে autosave recovered। কোনো quota/verification bypass বা alternate hidden API ব্যবহার হয়নি।

## Measured resource এবং cache

| বিষয় | প্রকৃত observation |
|---|---|
| GPU | Tesla T4; 15.00 GiB total, 14.56 GiB free at hardware probe |
| Compute capability / driver | 7.5 / 580.82.07 |
| System RAM | 12.67 GiB total; 11.47 GiB available at hardware probe |
| Disk | প্রায় 112.64 GiB total, প্রায় 112.53 GiB free at probe |
| Python / Torch | 3.13.16 / 2.14.1+cu130 |
| Transformers / Accelerate | 5.22.1 / 1.15.0 |
| `bitsandbytes` | অনুপস্থিত |
| Native isolation `bwrap` | অনুপস্থিত |
| Inspected model-weight files | ০ |
| Existing install receipts in isolated research store | shared ০; native ০ |
| GPU model processes at inspection | শূন্য |
| Paid plan / free quota | UI: not subscribed, zero compute units; free runtime connected। Remaining quota hours অজানা |

UI-র initial “up to 4 hours” এবং পরে কমে আসা session estimate guaranteed quota নয়।
Driver CUDA banner installed CUDA/model compatibility-এর প্রমাণ নয়। Actual model loading,
NF4/BF16 kernels ও numeric/runtime compatibility **NOT TESTED**।

Inspected cache roots: `/content`, `/root/.cache/huggingface/hub`, `/root/.cache/torch`,
`/workspace/models`, `/workspace/blank-app/phase3_models`। অন্য session বা owner device-এর
cache উপস্থিত ধরে নেওয়া হয়নি। কোনো model weights খোলা/hash/load/download করা হয়নি;
inventory-তে শুধু filename/size দেখা হয়েছে। Production database বা media খোলা হয়নি।

Raw shared probe-এ generic “not verified as Kaggle” provider label ও free-tier fields null
থাকে; helper account attestation করে না। সেগুলো অপরিবর্তিত রাখা হয়েছে। পৃথক authenticated
Chrome UI observation এবং actual `nvidia-smi` output Colab/T4 access প্রতিষ্ঠা করেছে।

## তিন stage-এর ফল

| Stage | Pinned candidate | Existing RAM planning gate | Actual result | Model calls / worker launches |
|---|---|---|---|---|
| 1 — YouTube AI | Qwen3.5 9B, NF4-on-load / FP16 compute | 16 GiB available | BLOCKED at RAM preflight | 0 / 0 |
| 2 — Music AI | ACE-Step 1.5 | 24 GiB available | BLOCKED at RAM preflight | 0 / 0 |
| 3 — Voice AI | Indic-Speak | 24 GiB available | BLOCKED at RAM preflight | 0 / 0 |

সব actual stage state-এর blocker:
`Available host/container RAM below conservative planning gate.`

এগুলো existing conservative, unmeasured planning gates; প্রকৃত minimum RAM বা এই GPU-তে
কোনো configuration কখনো চলতে পারবে না—এমন দাবি নয়। অনুমোদন/প্রমাণ ছাড়া gate কমানো হয়নি।
Stage call reservation-ও হয়নি: তিনটিতে `calls=[]`, `samples=[]`।

RAM gate বাদেও cached-only execution বর্তমানে অসম্ভব: inspected weights ও approved
install receipts অনুপস্থিত। Qwen NF4-এর `bitsandbytes` নেই। Music/Voice-এর isolated native
worker-এর `bwrap` নেই; সেটি সরিয়ে direct execution চালানো হয়নি। এই অতিরিক্ত বাধাগুলো
inspection থেকে জানা; worker launch করে এগুলো পরীক্ষা করা হয়েছে দাবি নয়।

## Exact model/download dependencies

| Model | Revision | Existing selected weight metadata |
|---|---|---|
| `Qwen/Qwen3.5-9B` | `c202236235762e1c871ad0ccb60c8ee5ba337b9a` | 19,306,310,880 bytes (~19.31 GB), plus configs/tokenizer |
| `ACE-Step/Ace-Step1.5` | `19671f406d603126926c1b7e2adc169acbcade22` | 10,029,206,151 bytes (~10.03 GB), plus configs/tokenizers/source/dependencies |
| `bodhan-ai/indic-speak` | `76e0814f189321efe550011850cd288dae366aad` | 7,068,852,569 bytes (~7.07 GB), plus approved SNAC and configs/tokenizer/source |

তিন profile-এ `download_approved=False`। এগুলো full source/selected recipes-এর metadata;
NF4 compute মানে ছোট GGUF download নয়। আগের Story GGUF inference এই YouTube NF4 case-এর
বিকল্প ফল বা model-install permission নয়। Indic-Speak repository source access-ও current
runtime weight/auxiliary/license receipt-এর বিকল্প নয়। কোনো নতুন license গ্রহণ করা হয়নি।

পরের execution-এর আগে যথাযথ RAM/gate-compliant free resource, exact approved local bundle
ও existing owner-reviewed installation receipts, compatible dependencies এবং কার্যকর native
isolation লাগবে। Missing download/component/license approval আলাদা থাকতে হবে। শুধু download
অনুমতি দিলেই বর্তমান RAM/isolation blockers দূর হবে না। Gate/precision/model recipe বদলাতে
হলে সেটি পৃথক অনুমোদিত ও evidence-based কাজ; এই পরীক্ষায় তা করা হয়নি।

## তিনটি পৃথক human-review document

Actual Colab harness তিনটি document লিখেছে, এবং সেগুলো হুবহু সংরক্ষিত:

1. `connected_colab_run/stage1/STAGE1_YOUTUBE_HUMAN_REVIEW_BN.md`
2. `connected_colab_run/stage2/STAGE2_MUSIC_HUMAN_REVIEW_BN.md`
3. `connected_colab_run/stage3/STAGE3_VOICE_HUMAN_REVIEW_BN.md`

এগুলো সব **NOT READY — no genuine generated samples**। Original briefs/cues/dialogue
authored inputs, model outputs নয়। কোনো generated title, music WAV বা voice WAV নেই;
usable listening/creative-review package সম্পন্ন দাবি করা হচ্ছে না। Human scores/acceptance
ফাঁকা, independent artistic approval ০। Model winner/production-ready promotion হয়নি।

## Evidence ও resume

Directory: `verification/real_stages_1_3_20261115/connected_colab_run/`।
Original hardware/cache text, JSON inventory, তিনটি actual `state.json`, তিনটি review document,
`execution_manifest.json`, SHA256 file manifest এবং readable Colab screenshot আছে।
Actual generated media নেই বলে private audio export/download করা হয়নি। GitHub-এ safe
research text/manifests এবং lightweight UI screenshot; model files/database/credentials নেই।

আগের successful engineering/regression/creative benchmark পুনরায় চালানো হয়নি; নতুন code
development বা software test rerun ছিল না। শুধু current requested execution gates ও captured
evidence consistency যাচাই হয়েছে। Director/Story/Script বা অন্য agent workstreams বদলায়নি।

পরের resume: এই feature checkpoint এবং তিনটি saved stage state পড়ে missing resource/cache/
receipt/isolation requirements মেটান; তারপর Stage 1 sample A-এর **প্রথম** actual canary।
তার technical result pass হলে পরের case; model release যাচাইয়ের পরে Stage 2, তারপর Stage 3।
বর্তমানে কোনো model call/captured sample আছে ধরে শুরু করবেন না।

Paid API/GPU/billing, model downloads, gate lowering, Render deployment, main modification
ও YouTube upload/publish/schedule — **সব ০**।
